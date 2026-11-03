"""Login, logout, account setup, password reset and password change."""
from datetime import datetime, timezone

from flask import Blueprint, current_app, flash, g, redirect, render_template, url_for

from extensions import db, limiter
from forms import ChangePasswordForm, ForgotForm, LoginForm, ProfileForm, SetPasswordForm
from mail import send_reset_link
from models import User
from security import (audit, check_login, end_all_sessions, find_token, hash_password, issue_token,
                      login_required, login_user, logout_user, password_problem)

bp = Blueprint("auth", __name__)

GENERIC_LOGIN_ERROR = "That email and password do not match an active account."


def home_for(user):
    return url_for("admin.dashboard") if user.is_admin else url_for("portal.dashboard")


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["LOGIN_RATE_LIMIT"], methods=["POST"])
def login():
    if g.get("user"):
        return redirect(home_for(g.user))
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = check_login(form.email.data, form.password.data)
        if user:
            login_user(user)
            audit("login", user=user)
            return redirect(home_for(user))   # fixed targets only, no ?next= (C10)
        error = GENERIC_LOGIN_ERROR           # same message whatever the reason (A6)
    expired = g.get("session_expired")
    return render_template("auth/login.html", form=form, error=error, expired=expired), (401 if error else 200)


@bp.route("/logout", methods=["POST"])
def logout():
    if g.get("user"):
        audit("logout")
    logout_user()
    flash("You have signed out.", "ok")
    return redirect(url_for("auth.login"))


@bp.route("/account/setup/<token>", methods=["GET", "POST"])
@limiter.limit("20 per hour", methods=["POST"])
def setup(token):
    tok = find_token(token)
    if tok is None:
        return render_template("auth/link_invalid.html"), 404
    form = SetPasswordForm()
    if form.validate_on_submit():
        problem = password_problem(form.password.data, tok.user.email)
        if problem:
            form.password.errors.append(problem)
        else:
            user = tok.user
            user.password_hash = hash_password(form.password.data)
            user.failed_logins, user.locked_until = 0, None
            end_all_sessions(user)
            tok.used_at = datetime.now(timezone.utc)
            db.session.commit()
            audit("password_set" if tok.purpose == "setup" else "password_reset", user=user)
            login_user(user)
            flash("Your password is saved. Welcome.", "ok")
            return redirect(home_for(user))
    return render_template("auth/set_password.html", form=form, purpose=tok.purpose, user=tok.user)


@bp.route("/account/forgot", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def forgot():
    form = ForgotForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.is_active and user.is_set_up:
            raw = issue_token(user, "reset")
            send_reset_link(user, url_for("auth.setup", token=raw, _external=True))
            audit("reset_requested", user=user)
        # Same response whether or not the account exists (A6).
        return render_template("auth/forgot_sent.html")
    return render_template("auth/forgot.html", form=form, mail_enabled=bool(current_app.config["SMTP_HOST"]))


@bp.route("/account/password", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per hour", methods=["POST"])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = g.user
        if not check_login(user.email, form.current.data):
            form.current.errors.append("Your current password is not right.")
        else:
            problem = password_problem(form.password.data, user.email)
            if problem:
                form.password.errors.append(problem)
            else:
                user.password_hash = hash_password(form.password.data)
                end_all_sessions(user)      # signs out other devices (A8, A12)
                db.session.commit()
                audit("password_changed")
                login_user(user)
                flash("Password changed. Other devices have been signed out.", "ok")
                return redirect(home_for(user))
    return render_template("auth/change_password.html", form=form)


@bp.route("/account/profile", methods=["GET", "POST"])
@login_required
@limiter.limit("30 per hour", methods=["POST"])
def profile():
    """Change the name (and organisation) shown on your account. Email changes go through an admin."""
    form = ProfileForm(obj=g.user)
    if form.validate_on_submit():
        g.user.name = form.name.data
        g.user.organisation = form.organisation.data or None
        db.session.commit()
        audit("profile_updated")
        flash("Profile saved.", "ok")
        return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", form=form)
