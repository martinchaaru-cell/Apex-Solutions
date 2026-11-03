"""Admin dashboard: enquiries, client accounts and documents. Admins only (B1, B2)."""
import csv
import io
from datetime import datetime, timedelta, timezone

from flask import Blueprint, Response, abort, flash, g, redirect, render_template, request, url_for
from sqlalchemy import func

from content import BUDGET_CHOICES, SERVICE_CHOICES
from extensions import db
from forms import ClientForm, ConfirmForm, DocumentEditForm, DocumentForm, StatusForm
from mail import send_setup_link
from models import AuditLog, Document, Enquiry, User
from security import audit, end_all_sessions, issue_token, role_required
from storage import UploadError, check_and_store, delete_file, human_size

bp = Blueprint("admin", __name__, url_prefix="/admin")

EAT = timezone(timedelta(hours=3), "EAT")   # Kenya: UTC+3 all year, no daylight saving


@bp.before_request
@role_required("admin")
def guard():
    """Every /admin route requires an admin, including any added later (deny by default)."""
    return None


@bp.app_template_filter("local")
def local_time(dt, fmt="%d %b %Y, %H:%M"):
    """Show a stored UTC time in Kenya time."""
    from models import aware
    return aware(dt).astimezone(EAT).strftime(fmt) if dt else ""


@bp.app_template_filter("filesize")
def filesize(n):
    return human_size(n)


def _neutralise(value):
    value = "" if value is None else str(value)
    return "'" + value if value[:1] in ("=", "+", "-", "@", "\t", "\r") else value


def _clients():
    return User.query.filter_by(role="client").order_by(func.lower(User.name)).all()


# --- Overview ---------------------------------------------------------------

@bp.route("/")
def dashboard():
    now = datetime.now(EAT)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    counts = dict(db.session.query(Enquiry.status, func.count()).group_by(Enquiry.status).all())
    pipeline = [(st, counts.get(st, 0)) for st in Enquiry.STATUSES]
    decided = counts.get("won", 0) + counts.get("lost", 0)
    by_service = (db.session.query(Enquiry.service, func.count()).group_by(Enquiry.service)
                  .order_by(func.count().desc()).limit(6).all())
    clients = User.query.filter_by(role="client")
    stats = {
        "new": counts.get("new", 0),
        "open": sum(counts.get(st, 0) for st in ("new", "contacted", "proposal sent")),
        "enquiries": sum(counts.values()),
        "month": Enquiry.query.filter(Enquiry.created_at >= month_start).count(),
        "win_rate": round(100 * counts.get("won", 0) / decided) if decided else None,
        "clients": clients.filter_by(is_active=True).count(),
        "pending": clients.filter(User.password_hash.is_(None), User.is_active.is_(True)).count(),
        "documents": Document.query.count(),
        "shared": Document.query.filter(Document.visibility != "admin").count(),
    }
    hour = now.hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
    return render_template(
        "admin/dashboard.html", stats=stats, pipeline=pipeline, by_service=by_service, greeting=greeting, today=now,
        waiting=Enquiry.query.filter_by(status="new").order_by(Enquiry.created_at.desc()).limit(5).all(),
        latest=Enquiry.query.order_by(Enquiry.created_at.desc()).limit(5).all(),
        recent_clients=clients.order_by(User.created_at.desc()).limit(4).all(),
        docs=Document.query.order_by(Document.created_at.desc()).limit(4).all(),
        activity=AuditLog.query.order_by(AuditLog.at.desc()).limit(8).all(),
        services=dict(SERVICE_CHOICES))


# --- Enquiries --------------------------------------------------------------

@bp.route("/enquiries")
def enquiries():
    status = request.args.get("status", "")
    q = Enquiry.query
    if status in Enquiry.STATUSES:
        q = q.filter_by(status=status)
    page = q.order_by(Enquiry.created_at.desc()).paginate(page=request.args.get("page", 1, type=int), per_page=25, max_per_page=25)
    counts = dict(db.session.query(Enquiry.status, func.count()).group_by(Enquiry.status).all())
    return render_template("admin/enquiries.html", page=page, status=status, counts=counts,
                           services=dict(SERVICE_CHOICES), budgets=dict(BUDGET_CHOICES))


@bp.route("/enquiries/<eid>", methods=["GET", "POST"])
def enquiry(eid):
    e = db.get_or_404(Enquiry, eid)
    form = StatusForm(obj=e)
    if form.validate_on_submit():
        e.status = form.status.data
        db.session.commit()
        audit("enquiry_status", f"{e.id} -> {e.status}")
        flash("Status updated.", "ok")
        return redirect(url_for("admin.enquiry", eid=e.id))
    return render_template("admin/enquiry.html", e=e, form=form, services=dict(SERVICE_CHOICES), budgets=dict(BUDGET_CHOICES))


@bp.route("/enquiries/export.csv")
def export_enquiries():
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["reference", "created_at", "status", "name", "email", "phone", "organisation", "service", "budget", "message"])
    for e in Enquiry.query.order_by(Enquiry.created_at.desc()).all():
        w.writerow([_neutralise(v) for v in (e.id, e.created_at.isoformat(), e.status, e.name, e.email, e.phone,
                                             e.organisation, e.service, e.budget, e.message)])
    audit("enquiries_exported")
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=apex-enquiries.csv", "Cache-Control": "no-store"})


# --- Clients ----------------------------------------------------------------

@bp.route("/clients")
def clients():
    return render_template("admin/clients.html", clients=_clients())


@bp.route("/clients/new", methods=["GET", "POST"])
def client_new():
    form = ClientForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        if User.query.filter_by(email=email).first():
            form.email.errors.append("An account with this email already exists.")
        else:
            user = User(name=form.name.data, email=email, organisation=form.organisation.data or None, role="client")
            db.session.add(user)
            db.session.commit()
            raw = issue_token(user, "setup")
            link = url_for("auth.setup", token=raw, _external=True)
            emailed = send_setup_link(user, link)
            audit("client_created", user.email)
            return render_template("admin/client_link.html", client=user, link=link, emailed=emailed, purpose="setup")
    return render_template("admin/client_form.html", form=form)


@bp.route("/clients/<uid>")
def client(uid):
    user = db.get_or_404(User, uid)
    if user.role != "client":
        abort(404)
    docs = Document.query.filter(
        (Document.visibility == "clients") | ((Document.visibility == "client") & (Document.client_id == user.id))
    ).order_by(Document.created_at.desc()).all()
    return render_template("admin/client.html", client=user, docs=docs, form=ConfirmForm())


@bp.route("/clients/<uid>/link", methods=["POST"])
def client_link(uid):
    user = db.get_or_404(User, uid)
    if user.role != "client" or not ConfirmForm().validate_on_submit():
        abort(400)
    purpose = "reset" if user.is_set_up else "setup"
    raw = issue_token(user, purpose)
    link = url_for("auth.setup", token=raw, _external=True)
    emailed = send_setup_link(user, link) if purpose == "setup" else False
    audit(f"{purpose}_link_created", user.email)
    return render_template("admin/client_link.html", client=user, link=link, emailed=emailed, purpose=purpose)


@bp.route("/clients/<uid>/toggle", methods=["POST"])
def client_toggle(uid):
    user = db.get_or_404(User, uid)
    if user.role != "client" or not ConfirmForm().validate_on_submit():
        abort(400)
    user.is_active = not user.is_active
    end_all_sessions(user)
    db.session.commit()
    audit("client_enabled" if user.is_active else "client_disabled", user.email)
    flash(f"{user.name} is now {'active' if user.is_active else 'disabled'}.", "ok")
    return redirect(url_for("admin.client", uid=user.id))


# --- Documents --------------------------------------------------------------

def _fill_clients(form):
    form.client_id.choices = [("", "Choose a client")] + [(u.id, f"{u.name} ({u.organisation or u.email})") for u in _clients()]


def _apply_sharing(doc, form):
    doc.visibility = form.visibility.data if form.visibility.data in Document.VISIBILITY else "admin"
    doc.client_id = None
    if doc.visibility == "client":
        client = db.session.get(User, form.client_id.data or "")
        if client is None or client.role != "client":
            return False
        doc.client_id = client.id
    return True


@bp.route("/documents")
def documents():
    docs = Document.query.order_by(Document.category, Document.title).all()
    return render_template("admin/documents.html", docs=docs, form=ConfirmForm())


@bp.route("/documents/upload", methods=["GET", "POST"])
def document_upload():
    form = DocumentForm()
    _fill_clients(form)
    if form.validate_on_submit():
        try:
            info = check_and_store(request.files.get("file"))
        except UploadError as err:
            form.file.errors = [str(err)]
        else:
            doc = Document(title=form.title.data, description=form.description.data or None,
                           category=form.category.data, uploaded_by=g.user.id, **info)
            if not _apply_sharing(doc, form):
                delete_file(doc)
                form.client_id.errors = ["Choose a valid client."]
            else:
                db.session.add(doc)
                db.session.commit()
                audit("document_uploaded", f"{doc.id} {doc.visibility}")
                flash(f"Uploaded {doc.title}.", "ok")
                return redirect(url_for("admin.documents"))
    return render_template("admin/document_form.html", form=form, doc=None)


@bp.route("/documents/<did>/edit", methods=["GET", "POST"])
def document_edit(did):
    doc = db.get_or_404(Document, did)
    form = DocumentEditForm(obj=doc)
    _fill_clients(form)
    if request.method == "GET":
        form.client_id.data = doc.client_id or ""
    if form.validate_on_submit():
        doc.title, doc.description, doc.category = form.title.data, form.description.data or None, form.category.data
        if not _apply_sharing(doc, form):
            form.client_id.errors = ["Choose a valid client."]
        else:
            db.session.commit()
            audit("document_updated", f"{doc.id} {doc.visibility}")
            flash("Document updated.", "ok")
            return redirect(url_for("admin.documents"))
    return render_template("admin/document_form.html", form=form, doc=doc)


@bp.route("/documents/<did>/delete", methods=["POST"])
def document_delete(did):
    doc = db.get_or_404(Document, did)
    if not ConfirmForm().validate_on_submit():
        abort(400)
    delete_file(doc)
    db.session.delete(doc)
    db.session.commit()
    audit("document_deleted", doc.id)
    flash(f"Deleted {doc.title}.", "ok")
    return redirect(url_for("admin.documents"))


@bp.route("/activity")
def activity():
    page = AuditLog.query.order_by(AuditLog.at.desc()).paginate(page=request.args.get("page", 1, type=int), per_page=50, max_per_page=50)
    return render_template("admin/activity.html", page=page)
