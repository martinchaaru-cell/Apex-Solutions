"""Database models. Only the fields each feature needs (Baseline E2). Public IDs are UUIDs (B9)."""
import uuid
from datetime import datetime, timezone

from extensions import db


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


def aware(dt):
    """SQLite returns naive datetimes; treat stored values as UTC."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class Enquiry(db.Model):
    __tablename__ = "enquiries"

    STATUSES = ["new", "contacted", "proposal sent", "won", "lost", "closed"]

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, index=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    phone = db.Column(db.String(32))
    organisation = db.Column(db.String(160))
    service = db.Column(db.String(40), nullable=False)
    budget = db.Column(db.String(40), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="new")


class User(db.Model):
    __tablename__ = "users"

    ROLES = ("admin", "client")

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    organisation = db.Column(db.String(160))
    role = db.Column(db.String(10), nullable=False, default="client")
    password_hash = db.Column(db.String(255))          # empty until the account is set up
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    last_login_at = db.Column(db.DateTime(timezone=True))
    failed_logins = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime(timezone=True))
    session_version = db.Column(db.Integer, nullable=False, default=1)  # bump to end all sessions (A7, A8)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_set_up(self):
        return bool(self.password_hash)


class Token(db.Model):
    """One-time links for account setup and password reset. Only a hash is stored (A7)."""
    __tablename__ = "tokens"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    purpose = db.Column(db.String(10), nullable=False)   # "setup" or "reset"
    token_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used_at = db.Column(db.DateTime(timezone=True))

    user = db.relationship("User")


class Document(db.Model):
    """An uploaded file. Stored outside the web root and served only through a checked route (B8)."""
    __tablename__ = "documents"

    VISIBILITY = {"admin": "Admin only", "clients": "All clients", "client": "One client"}
    CATEGORIES = ["Agreements", "Proposals and templates", "Guides", "Security", "Project files", "Other"]

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.String(500))
    category = db.Column(db.String(40), nullable=False, default="Other")
    original_name = db.Column(db.String(200), nullable=False)
    stored_name = db.Column(db.String(80), nullable=False, unique=True)
    extension = db.Column(db.String(8), nullable=False)
    mimetype = db.Column(db.String(120), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    sha256 = db.Column(db.String(64), nullable=False, index=True)
    visibility = db.Column(db.String(10), nullable=False, default="admin")
    client_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"))
    uploaded_by = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, index=True)

    client = db.relationship("User", foreign_keys=[client_id])

    def visible_to(self, user):
        """Object-level permission check (B3). Admins see everything; clients see shared files only."""
        if user is None or not user.is_active:
            return False
        if user.is_admin:
            return True
        if self.visibility == "clients":
            return True
        return self.visibility == "client" and self.client_id == user.id


class AuditLog(db.Model):
    """Security and admin events (J1). Never stores passwords, tokens or file contents (J2)."""
    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    at = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"))
    action = db.Column(db.String(40), nullable=False)
    target = db.Column(db.String(200))
    ip = db.Column(db.String(64))

    user = db.relationship("User")
