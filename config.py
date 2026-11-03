"""Configuration. Every secret and contact detail comes from the environment (Baseline D1)."""
import os


def _bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class Config:
    ENV_NAME = os.environ.get("APP_ENV", "production")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///apex-dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Cookies (A8 / G4). Secure is on unless explicitly running local HTTP.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("COOKIE_SECURE", True)
    SESSION_COOKIE_NAME = "apex_session"

    # PREVIEW_MODE is for the Replit Preview pane only, which shows the site inside a
    # frame on replit.com. It allows that one framing parent and lets the form cookie
    # work inside the frame. Never set it on the live server.
    PREVIEW_MODE = _bool("PREVIEW_MODE", False)
    PREVIEW_FRAME_ANCESTORS = "https://replit.com https://*.replit.com https://*.replit.dev https://*.repl.co"
    if PREVIEW_MODE:
        SESSION_COOKIE_SAMESITE = "None"
        SESSION_COOKIE_SECURE = True
        SESSION_COOKIE_PARTITIONED = True
    WTF_CSRF_TIME_LIMIT = 3600
    # Request size: forms stay small; only the admin document upload may be large.
    MAX_FORM_BYTES = 64 * 1024
    MAX_DOCUMENT_MB = int(os.environ.get("MAX_DOCUMENT_MB", "20"))
    MAX_CONTENT_LENGTH = (MAX_DOCUMENT_MB + 1) * 1024 * 1024
    DOCUMENTS_FOLDER = os.environ.get("DOCUMENTS_FOLDER", "")   # default: instance/documents (outside static)

    # Accounts (Security Baseline A5, A7, A8)
    LOGIN_RATE_LIMIT = os.environ.get("LOGIN_RATE_LIMIT", "10 per minute;50 per hour")
    LOCKOUT_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15
    ADMIN_IDLE_MINUTES = 15
    CLIENT_IDLE_MINUTES = 30
    SESSION_ABSOLUTE_HOURS = 8
    SETUP_LINK_HOURS = 48
    RESET_LINK_MINUTES = 30

    # Rate limits (F2). Use redis:// in production when running several workers.
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True
    CONTACT_RATE_LIMIT = os.environ.get("CONTACT_RATE_LIMIT", "5 per hour;20 per day")

    BEHIND_PROXY = _bool("BEHIND_PROXY", True)

    SITE_URL = os.environ.get("SITE_URL", "https://apexsolutions.co.ke").rstrip("/")

    # Public contact details. Left blank = hidden on the site (copy rule 4).
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "")
    WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "")  # digits only, e.g. 2547XXXXXXXX
    LOCATION_TEXT = os.environ.get("LOCATION_TEXT", "Based in Kenya. Working with clients on site and remotely.")
    SECURITY_CONTACT = os.environ.get("SECURITY_CONTACT", "")

    # Optional enquiry notification email (G8: fixed From and To).
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    MAIL_FROM = os.environ.get("MAIL_FROM", "")
    MAIL_TO = os.environ.get("MAIL_TO", "")

    ENQUIRY_RETENTION_DAYS = int(os.environ.get("ENQUIRY_RETENTION_DAYS", "730"))


class TestConfig(Config):
    ENV_NAME = "test"
    TESTING = True
    SECRET_KEY = "test-only-not-a-secret-0123456789abcdef"  # nosec B105
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SESSION_COOKIE_SECURE = False
    RATELIMIT_STORAGE_URI = "memory://"
    BEHIND_PROXY = False
    PREVIEW_MODE = False
    DOCUMENTS_FOLDER = ""
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_PARTITIONED = False
