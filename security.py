"""Login, sessions, one-time links, role checks and audit logging (Security Baseline A, B, J)."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import abort, current_app, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import AuditLog, Token, User, aware

# --- Passwords (A1, A2) ------------------------------------------------------

MIN_PASSWORD = 12
MAX_PASSWORD = 128
COMMON = {
    "password", "password1", "password123", "password1234", "passw0rd", "qwerty", "qwerty123", "qwertyuiop",
    "123456789012", "12345678", "123456789", "1234567890", "111111111111", "iloveyou", "welcome123",
    "admin123456", "letmein123", "kenya2026", "nairobi2026", "apex2026", "apexsolutions", "changeme123",
}
# Precomputed hash used when an email is unknown, so failed logins take similar time (A6).
_DUMMY_HASH = generate_password_hash("not-a-real-password-for-timing-only")


def password_problem(password, email=""):
    """Return a plain-language reason the password is not allowed, or None."""
    if len(password) < MIN_PASSWORD:
        return f"Use at least {MIN_PASSWORD} characters. A short phrase of three or four words works well."
    if len(password) > MAX_PASSWORD:
        return f"Use no more than {MAX_PASSWORD} characters."
    lowered = password.lower()
    if lowered in COMMON or lowered.rstrip("!0123456789") in COMMON:
        return "That password is too common. Choose something less predictable."
    if len(set(password)) < 5:
        return "That password repeats too few characters. Choose something less predictable."
    local = email.split("@")[0].lower()
    if local and len(local) >= 4 and local in lowered:
        return "Do not include your email address in your password."
    return None


def hash_password(password):
    return generate_password_hash(password, method="scrypt")  # scrypt with per-user salt (A1)


# --- One-time links (A3, A7) -------------------------------------------------

def _digest(raw):
    return hashlib.sha256(raw.encode()).hexdigest()


def issue_token(user, purpose):
    """Create a single-use link token; only its hash is stored. Older unused tokens are cancelled."""
    hours = current_app.config["SETUP_LINK_HOURS"] if purpose == "setup" else 0
    minutes = current_app.config["RESET_LINK_MINUTES"] if purpose == "reset" else 0
    now = datetime.now(timezone.utc)
    Token.query.filter_by(user_id=user.id, purpose=purpose, used_at=None).update({"used_at": now})
    raw = secrets.token_urlsafe(32)  # 256 bits
    db.session.add(Token(user_id=user.id, purpose=purpose, token_hash=_digest(raw),
                         expires_at=now + timedelta(hours=hours, minutes=minutes)))
    db.session.commit()
    return raw


def find_token(raw):
    """Return the valid, unused Token for a raw link value, or None."""
    if not raw or len(raw) > 100:
        return None
    tok = Token.query.filter_by(token_hash=_digest(raw)).first()
    if not tok or tok.used_at or aware(tok.expires_at) < datetime.now(timezone.utc):
        return None
    if not tok.user or not tok.user.is_active:
        return None
    return tok


# --- Sessions (A8) -----------------------------------------------------------

def login_user(user):
    session.clear()                      # fresh session at login (fixation)
    session.permanent = False
    now = int(datetime.now(timezone.utc).timestamp())
    session.update(uid=user.id, sv=user.session_version, iat=now, seen=now)
    user.last_login_at = datetime.now(timezone.utc)
    user.failed_logins = 0
    user.locked_until = None
    db.session.commit()


def logout_user():
    session.clear()


def end_all_sessions(user):
    """Invalidate every session for this user, for example after a password change."""
    user.session_version = (user.session_version or 1) + 1


def load_current_user():
    """Run before each request. Sets g.user, enforcing idle and absolute timeouts."""
    g.user = None
    uid = session.get("uid")
    if not uid:
        return
    user = db.session.get(User, uid)
    now = int(datetime.now(timezone.utc).timestamp())
    cfg = current_app.config
    idle = cfg["ADMIN_IDLE_MINUTES"] if user and user.is_admin else cfg["CLIENT_IDLE_MINUTES"]
    expired = (
        user is None or not user.is_active or session.get("sv") != user.session_version
        or now - session.get("seen", 0) > idle * 60
        or now - session.get("iat", 0) > cfg["SESSION_ABSOLUTE_HOURS"] * 3600
    )
    if expired:
        session.clear()
        g.session_expired = True
        return
    session["seen"] = now
    g.user = user


def role_required(role):
    """Deny by default: the route needs a logged-in user with this role (B1, B2)."""
    def deco(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.get("user") is None:
                return redirect(url_for("auth.login"))
            if g.user.role != role:
                audit("access_denied", request.path)
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return deco


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.get("user") is None:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


# --- Login checks (A5, A6) ---------------------------------------------------

def check_login(email, password):
    """Return the User if the email and password are right and the account is usable, else None."""
    user = User.query.filter_by(email=email.strip().lower()).first()
    now = datetime.now(timezone.utc)
    if user is None or not user.password_hash:
        check_password_hash(_DUMMY_HASH, password)
        return None
    if not user.is_active or (user.locked_until and aware(user.locked_until) > now):
        check_password_hash(_DUMMY_HASH, password)
        audit("login_blocked", user.email, user=user)
        return None
    if not check_password_hash(user.password_hash, password):
        user.failed_logins = (user.failed_logins or 0) + 1
        if user.failed_logins >= current_app.config["LOCKOUT_ATTEMPTS"]:
            user.locked_until = now + timedelta(minutes=current_app.config["LOCKOUT_MINUTES"])
            user.failed_logins = 0
            audit("account_locked", user.email, user=user)
        db.session.commit()
        audit("login_failed", user.email, user=user)
        return None
    return user


# --- Audit (J1, J2) ----------------------------------------------------------

def audit(action, target="", user=None):
    who = user or g.get("user")
    db.session.add(AuditLog(user_id=who.id if who else None, action=action,
                            target=(target or "")[:200], ip=(request.remote_addr or "")[:64]))
    db.session.commit()
    # Server log gets the event and user ID only; details stay in the database (J2).
    current_app.logger.info("audit %s user=%s", action, who.id if who else "-")
