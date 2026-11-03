"""Apex Solutions website, admin dashboard and client portal (Security Baseline Level 2).

Run locally:   flask --app app run
Production:    gunicorn wsgi:app
"""
import csv
import hashlib
import logging
import os
import secrets
import shutil
import uuid
from datetime import datetime, timedelta, timezone

import click
from flask import Flask, abort, g, render_template, request
from flask_wtf.csrf import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from extensions import csrf, db, limiter
from models import Document, Enquiry, User

CSP = "; ".join([
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "object-src 'none'",
    "upgrade-insecure-requests",
])

PRIVATE_PREFIXES = ("/admin", "/portal", "/account", "/login", "/documents")
UPLOAD_ENDPOINTS = {"admin.document_upload"}


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_object)

    if not app.config.get("SECRET_KEY") or len(app.config["SECRET_KEY"]) < 32:
        # D6: refuse to start with a missing or weak key rather than run insecurely.
        raise RuntimeError("SECRET_KEY must be set to a random value of at least 32 characters.")

    if not app.config.get("DOCUMENTS_FOLDER"):
        app.config["DOCUMENTS_FOLDER"] = os.path.join(app.instance_path, "documents")

    if app.config.get("BEHIND_PROXY"):
        # A reverse proxy sits in front: trust exactly one hop so rate limits see the visitor's real IP.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if app.config.get("PREVIEW_MODE"):
        app.logger.warning("PREVIEW_MODE is on: framing by replit.com is allowed. Do not use on the live site.")

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    import admin
    import auth
    import portal
    import routes
    from security import load_current_user

    app.register_blueprint(routes.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(portal.bp)

    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()

    @app.before_request
    def before():
        # Only the document upload may send a large body; everything else stays small.
        if (request.content_length or 0) > app.config["MAX_FORM_BYTES"] and request.endpoint not in UPLOAD_ENDPOINTS:
            abort(413)
        load_current_user()

    @app.context_processor
    def inject_user():
        return {"current_user": g.get("user")}

    @app.after_request
    def security_headers(resp):  # G1, G7, E6
        resp.headers["X-Content-Type-Options"] = "nosniff"
        if app.config.get("PREVIEW_MODE"):
            resp.headers["Content-Security-Policy"] = CSP.replace(
                "frame-ancestors 'none'", "frame-ancestors " + app.config["PREVIEW_FRAME_ANCESTORS"])
        else:
            resp.headers["Content-Security-Policy"] = CSP
            resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        if request.path.startswith(PRIVATE_PREFIXES) or request.endpoint in {"site.contact", "site.contact_thanks"}:
            resp.headers["Cache-Control"] = "no-store"
        if request.path.startswith(PRIVATE_PREFIXES):
            resp.headers["X-Robots-Tag"] = "noindex, nofollow"
        resp.headers.pop("Server", None)
        return resp

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403, title="Not available",
                               message="Your account does not have access to that page."), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, title="Page not found",
                               message="That page does not exist or has moved."), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template("error.html", code=413, title="Too large",
                               message=f"That upload is too large. Files can be up to {app.config['MAX_DOCUMENT_MB']} MB."), 413

    @app.errorhandler(429)
    def too_many(e):
        return render_template("error.html", code=429, title="Too many requests",
                               message="There have been several attempts in a short time. Please wait and try again later."), 429

    @app.errorhandler(CSRFError)
    def csrf_error(e):
        return render_template("error.html", code=400, title="Form expired",
                               message="Your form session expired. Please go back, refresh the page and try again."), 400

    @app.errorhandler(500)
    def server_error(e):  # D7: generic message, details only in server logs
        return render_template("error.html", code=500, title="Something went wrong",
                               message="We could not complete that request. Please try again shortly."), 500

    _register_cli(app)
    return app


def _neutralise(value):
    """C11: stop spreadsheet formula injection in exports."""
    value = "" if value is None else str(value)
    return "'" + value if value[:1] in ("=", "+", "-", "@", "\t", "\r") else value


def _seed_category(name):
    n = name.lower()
    if "agreement" in n:
        return "Agreements"
    if "template" in n or "questionnaire" in n or "worked_example" in n:
        return "Proposals and templates"
    if "security" in n:
        return "Security"
    return "Guides"


def _register_cli(app):
    from security import hash_password, issue_token, password_problem

    @app.cli.command("create-admin")
    @click.option("--email", prompt="Admin email")
    @click.option("--name", prompt="Admin name")
    @click.password_option("--password", prompt="Password (at least 12 characters)")
    def create_admin(email, name, password):
        """Create the first admin account (Baseline A10: no default accounts)."""
        email = email.strip().lower()
        problem = password_problem(password, email)
        if problem:
            raise click.ClickException(problem)
        if User.query.filter_by(email=email).first():
            raise click.ClickException("An account with that email already exists.")
        db.session.add(User(email=email, name=name.strip(), role="admin", password_hash=hash_password(password)))
        db.session.commit()
        click.echo(f"Admin account created for {email}. Sign in at /login.")

    @app.cli.command("ensure-admin")
    def ensure_admin():
        """Create the admin from the ADMIN_EMAIL and ADMIN_PASSWORD secrets, once.

        If the account already exists nothing changes, so a password you later change
        in the dashboard is never overwritten by the secret.
        """
        email = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
        password = os.environ.get("ADMIN_PASSWORD") or ""
        if not email or not password:
            click.echo("ADMIN_EMAIL / ADMIN_PASSWORD not set: skipping.")
            return
        if User.query.filter_by(email=email).first():
            click.echo(f"Admin {email} already exists: the ADMIN_PASSWORD secret is not used and can be deleted.")
            return
        if "@" not in email or len(email) > 254:
            raise click.ClickException("ADMIN_EMAIL is not a valid email address.")
        problem = password_problem(password, email)
        if problem:
            raise click.ClickException(f"ADMIN_PASSWORD was not accepted: {problem}")
        name = (os.environ.get("ADMIN_NAME") or "Administrator").strip()[:120] or "Administrator"
        db.session.add(User(email=email, name=name, role="admin", password_hash=hash_password(password)))
        db.session.commit()
        click.echo(f"Admin account created for {email}. Sign in at /login.")

    @app.cli.command("admin-reset-link")
    @click.argument("email")
    def admin_reset_link(email):
        """Print a one-time password reset link for any account (if you are locked out)."""
        user = User.query.filter_by(email=email.strip().lower()).first()
        if not user:
            raise click.ClickException("No account with that email.")
        raw = issue_token(user, "reset" if user.is_set_up else "setup")
        click.echo(f"{app.config['SITE_URL']}/account/setup/{raw}")

    @app.cli.command("import-seed-documents")
    @click.option("--folder", default="seed_documents")
    def import_seed_documents(folder):
        """Import files from seed_documents/ as admin-only documents.

        Files already imported are skipped. If a seed file with the same name has changed
        (for example a new version with the logo header), the stored copy is replaced.
        """
        from storage import ALLOWED, delete_file, folder as docs_folder, safe_display_name
        if not os.path.isdir(folder):
            click.echo("No seed folder found.")
            return
        added = updated = 0
        for name in sorted(os.listdir(folder)):
            ext = name.rsplit(".", 1)[-1].lower()
            if ext not in ALLOWED:
                continue
            with open(os.path.join(folder, name), "rb") as f:
                data = f.read()
            digest = hashlib.sha256(data).hexdigest()
            if Document.query.filter_by(sha256=digest).first():
                continue
            stored = f"{uuid.uuid4().hex}.{ext}"
            dest = os.path.join(docs_folder(), stored)
            shutil.copyfile(os.path.join(folder, name), dest)
            os.chmod(dest, 0o600)
            display = safe_display_name(name)
            old = Document.query.filter_by(original_name=display, uploaded_by=None).first()
            if old:   # a newer version of a seed file: keep its sharing settings, swap the file
                delete_file(old)
                old.stored_name, old.size, old.sha256 = stored, len(data), digest
                updated += 1
                continue
            title = name.rsplit(".", 1)[0].replace("_", " ")
            db.session.add(Document(title=title, category=_seed_category(name), original_name=display,
                                    stored_name=stored, extension=ext, mimetype=ALLOWED[ext], size=len(data),
                                    sha256=digest, visibility="admin"))
            added += 1
        db.session.commit()
        click.echo(f"Imported {added} new and updated {updated} document(s). New ones are admin-only.")

    @app.cli.command("export-enquiries")
    @click.argument("path")
    def export_enquiries(path):
        """Export enquiries to a CSV file (formula-safe)."""
        rows = Enquiry.query.order_by(Enquiry.created_at.desc()).all()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["reference", "created_at", "name", "email", "phone", "organisation", "service", "budget", "status", "message"])
            for e in rows:
                w.writerow([_neutralise(v) for v in (e.id, e.created_at.isoformat(), e.name, e.email, e.phone,
                                                     e.organisation, e.service, e.budget, e.status, e.message)])
        click.echo(f"Exported {len(rows)} enquiries to {path}")

    @app.cli.command("purge-enquiries")
    def purge_enquiries():
        """Delete enquiries older than ENQUIRY_RETENTION_DAYS (E8)."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=app.config["ENQUIRY_RETENTION_DAYS"])
        n = Enquiry.query.filter(Enquiry.created_at < cutoff).delete()
        db.session.commit()
        click.echo(f"Deleted {n} enquiries older than {cutoff.date()}")

    @app.cli.command("delete-enquiry")
    @click.argument("email")
    def delete_enquiry(email):
        """Delete all enquiries from one email address (data subject request)."""
        n = Enquiry.query.filter(db.func.lower(Enquiry.email) == email.strip().lower()).delete()
        db.session.commit()
        click.echo(f"Deleted {n} enquiries for that address")

    @app.cli.command("gen-secret")
    def gen_secret():
        """Print a new random SECRET_KEY."""
        click.echo(secrets.token_urlsafe(48))
