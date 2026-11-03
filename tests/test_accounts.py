"""Accounts, dashboards and documents (Security Baseline Level 2: A, B, C5, F, J)."""
import io
import re
import zipfile
from datetime import datetime, timedelta, timezone

import pytest

from app import create_app
from config import TestConfig
from extensions import db, limiter
from models import AuditLog, Document, Token, User
from security import hash_password, issue_token

PW = "correct horse battery staple"


class Cfg(TestConfig):
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app(tmp_path):
    class C(Cfg):
        DOCUMENTS_FOLDER = str(tmp_path / "docs")
    app = create_app(C)
    limiter.reset()
    with app.app_context():
        admin = User(email="admin@apex.test", name="Admin User", role="admin", password_hash=hash_password(PW))
        alice = User(email="alice@client.test", name="Alice Client", role="client", password_hash=hash_password(PW))
        bob = User(email="bob@client.test", name="Bob Client", role="client", password_hash=hash_password(PW))
        db.session.add_all([admin, alice, bob])
        db.session.commit()
        app.ids = {"admin": admin.id, "alice": alice.id, "bob": bob.id}
    yield app
    with app.app_context():
        db.drop_all()


def login(client, email, password=PW):
    return client.post("/login", data={"email": email, "password": password})


def pdf_bytes():
    return b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


def docx_bytes(macro=False):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", "<w:document/>")
        if macro:
            z.writestr("word/vbaProject.bin", b"\x00")
    return buf.getvalue()


def upload(client, data, name, visibility="admin", client_id=""):
    return client.post("/admin/documents/upload", content_type="multipart/form-data", data={
        "title": "Test document", "description": "", "category": "Agreements",
        "visibility": visibility, "client_id": client_id, "file": (io.BytesIO(data), name)})


def make_doc(app, visibility, client_key=None):
    client = app.test_client()
    login(client, "admin@apex.test")
    r = upload(client, pdf_bytes(), "Agreement.pdf", visibility, app.ids.get(client_key, "") if client_key else "")
    assert r.status_code == 302, r.data[:400]
    with app.app_context():
        return Document.query.order_by(Document.created_at.desc()).first().id


# --- Authentication (A1, A5, A6, A8, A10) ---------------------------------

def test_passwords_are_hashed(app):
    with app.app_context():
        h = db.session.get(User, app.ids["admin"]).password_hash
        assert h.startswith("scrypt:") and PW not in h


def test_admin_login_goes_to_admin(app):
    r = login(app.test_client(), "admin@apex.test")
    assert r.status_code == 302 and r.headers["Location"].endswith("/admin/")


def test_client_login_goes_to_portal(app):
    r = login(app.test_client(), "alice@client.test")
    assert r.status_code == 302 and r.headers["Location"].endswith("/portal/")


def test_same_error_for_unknown_user_and_wrong_password(app):
    c = app.test_client()
    a = login(c, "nobody@apex.test").get_data(as_text=True)
    b = login(c, "alice@client.test", "wrong password here").get_data(as_text=True)
    msg = "That email and password do not match an active account."
    assert msg in a and msg in b


def test_lockout_after_repeated_failures(app):
    c = app.test_client()
    for _ in range(5):
        login(c, "bob@client.test", "wrong password here")
    assert login(c, "bob@client.test").status_code == 401   # right password, but locked
    with app.app_context():
        assert db.session.get(User, app.ids["bob"]).locked_until is not None


def test_login_rate_limited(app):
    c = app.test_client()
    codes = [login(c, "x@apex.test", "wrong password here").status_code for _ in range(11)]
    assert codes[-1] == 429


def test_session_cookie_flags():
    class Secure(Cfg):
        SESSION_COOKIE_SECURE = True
    app = create_app(Secure)
    limiter.reset()
    with app.app_context():
        db.session.add(User(email="s@apex.test", name="S", role="client", password_hash=hash_password(PW)))
        db.session.commit()
    r = login(app.test_client(), "s@apex.test")
    cookie = r.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "Secure" in cookie and "SameSite=Lax" in cookie


def test_logout_ends_session(app):
    c = app.test_client()
    login(c, "alice@client.test")
    assert c.get("/portal/").status_code == 200
    c.post("/logout")
    assert c.get("/portal/").status_code == 302


def test_disabled_account_is_signed_out(app):
    c = app.test_client()
    login(c, "alice@client.test")
    with app.app_context():
        u = db.session.get(User, app.ids["alice"])
        u.is_active = False
        u.session_version += 1
        db.session.commit()
    assert c.get("/portal/").status_code == 302


def test_idle_timeout(app):
    c = app.test_client()
    login(c, "alice@client.test")
    with c.session_transaction() as s:
        s["seen"] -= 31 * 60
    assert c.get("/portal/").status_code == 302


def test_password_policy(app):
    c = app.test_client()
    login(c, "alice@client.test")
    for bad in ["short1", "password1234", "aaaaaaaaaaaaaaaa", "alice-is-great-2026"]:
        r = c.post("/account/password", data={"current": PW, "password": bad, "confirm": bad})
        assert r.status_code == 200 and b"Password changed" not in r.data, bad


def test_change_password_ends_other_sessions(app):
    other = app.test_client()
    login(other, "alice@client.test")
    c = app.test_client()
    login(c, "alice@client.test")
    new = "a much longer river stone phrase"
    r = c.post("/account/password", data={"current": PW, "password": new, "confirm": new})
    assert r.status_code == 302
    assert other.get("/portal/").status_code == 302      # the other device is signed out
    assert c.get("/portal/").status_code == 200          # this one stays signed in


def test_no_default_accounts():
    app = create_app(Cfg)
    with app.app_context():
        assert User.query.count() == 0


# --- Setup and reset links (A3, A7) ------------------------------------------

def test_setup_link_single_use(app):
    with app.app_context():
        u = User(email="new@client.test", name="New Client", role="client")
        db.session.add(u)
        db.session.commit()
        raw = issue_token(u, "setup")
        assert Token.query.filter_by(token_hash=raw).first() is None   # only the hash is stored
    c = app.test_client()
    pw = "blue mountain coffee morning"
    r = c.post(f"/account/setup/{raw}", data={"password": pw, "confirm": pw})
    assert r.status_code == 302 and r.headers["Location"].endswith("/portal/")
    assert app.test_client().get(f"/account/setup/{raw}").status_code == 404


def test_expired_link_rejected(app):
    with app.app_context():
        u = db.session.get(User, app.ids["bob"])
        raw = issue_token(u, "reset")
        t = Token.query.filter_by(user_id=u.id, used_at=None).first()
        t.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.session.commit()
    assert app.test_client().get(f"/account/setup/{raw}").status_code == 404


def test_forgot_password_same_response(app):
    c = app.test_client()
    a = c.post("/account/forgot", data={"email": "alice@client.test"}).get_data(as_text=True)
    b = c.post("/account/forgot", data={"email": "nobody@client.test"}).get_data(as_text=True)
    assert re.sub(r"\s+", " ", a) == re.sub(r"\s+", " ", b)


# --- Authorisation matrix (B1, B2, B3) ---------------------------------------

ADMIN_PAGES = ["/admin/", "/admin/enquiries", "/admin/clients", "/admin/clients/new", "/admin/documents",
               "/admin/documents/upload", "/admin/activity", "/admin/enquiries/export.csv"]


@pytest.mark.parametrize("path", ADMIN_PAGES + ["/portal/", "/account/password"])
def test_logged_out_is_sent_to_login(app, path):
    r = app.test_client().get(path)
    assert r.status_code == 302 and "/login" in r.headers["Location"]


@pytest.mark.parametrize("path", ADMIN_PAGES)
def test_client_cannot_open_admin(app, path):
    c = app.test_client()
    login(c, "alice@client.test")
    assert c.get(path).status_code == 403


@pytest.mark.parametrize("path", ADMIN_PAGES)
def test_admin_can_open_admin(app, path):
    c = app.test_client()
    login(c, "admin@apex.test")
    assert c.get(path).status_code == 200


def test_admin_cannot_use_client_portal(app):
    c = app.test_client()
    login(c, "admin@apex.test")
    assert c.get("/portal/").status_code == 403


def test_client_cannot_post_admin_actions(app):
    c = app.test_client()
    login(c, "alice@client.test")
    assert upload(c, pdf_bytes(), "x.pdf").status_code == 403
    assert c.post(f"/admin/clients/{app.ids['bob']}/toggle").status_code == 403


@pytest.mark.parametrize("visibility,owner,alice,bob", [
    ("admin", None, 404, 404),
    ("clients", None, 200, 200),
    ("client", "alice", 200, 404),
])
def test_document_download_matrix(app, visibility, owner, alice, bob):
    did = make_doc(app, visibility, owner)
    for email, expected in [("alice@client.test", alice), ("bob@client.test", bob), ("admin@apex.test", 200)]:
        c = app.test_client()
        login(c, email)
        r = c.get(f"/documents/{did}/download")
        assert r.status_code == expected, (email, visibility)
        if expected == 200:
            assert r.headers["Content-Disposition"].startswith("attachment")
            assert r.headers["Cache-Control"] == "no-store"
    assert app.test_client().get(f"/documents/{did}/download").status_code == 302


def test_portal_lists_only_own_documents(app):
    mine = make_doc(app, "client", "alice")
    c = app.test_client()
    login(c, "bob@client.test")
    assert mine.encode() not in c.get("/portal/").data


def test_downloads_are_logged(app):
    did = make_doc(app, "clients")
    c = app.test_client()
    login(c, "alice@client.test")
    c.get(f"/documents/{did}/download")
    with app.app_context():
        assert AuditLog.query.filter_by(action="document_downloaded", target=did).count() == 1


# --- Uploads (C5, C9) -------------------------------------------------------

@pytest.fixture
def admin_client(app):
    c = app.test_client()
    login(c, "admin@apex.test")
    return c


def test_valid_pdf_and_docx_accepted(app, admin_client):
    assert upload(admin_client, pdf_bytes(), "Guide.pdf").status_code == 302
    assert upload(admin_client, docx_bytes(), "Agreement.docx").status_code == 302
    with app.app_context():
        docs = Document.query.all()
        assert len(docs) == 2
        for d in docs:
            assert re.fullmatch(r"[0-9a-f]{32}\.(pdf|docx)", d.stored_name)   # random server-side name


@pytest.mark.parametrize("data,name", [
    (b"MZ\x90\x00 fake exe", "tool.exe"),
    (b"<html><script>alert(1)</script></html>", "page.html"),
    (b"<html><script>alert(1)</script></html>", "fake.pdf"),
    (b"<svg onload=alert(1)>", "image.svg"),
    (b"%PDF-1.4", "double.pdf.exe"),
    (b"PK\x03\x04 not really a zip", "broken.docx"),
])
def test_bad_uploads_rejected(app, admin_client, data, name):
    r = upload(admin_client, data, name)
    assert r.status_code == 200 and b"err" in r.data
    with app.app_context():
        assert Document.query.count() == 0


def test_macro_document_rejected(app, admin_client):
    r = upload(admin_client, docx_bytes(macro=True), "Agreement.docx")
    assert r.status_code == 200
    with app.app_context():
        assert Document.query.count() == 0


def test_oversize_upload_rejected(app, admin_client):
    big = b"%PDF-" + b"0" * (app.config["MAX_DOCUMENT_MB"] * 1024 * 1024 + 10)
    assert upload(admin_client, big, "huge.pdf").status_code in (200, 413)
    with app.app_context():
        assert Document.query.count() == 0


def test_path_in_filename_is_neutralised(app, admin_client):
    upload(admin_client, pdf_bytes(), "../../etc/passwd.pdf")
    with app.app_context():
        d = Document.query.one()
        assert "/" not in d.original_name and ".." not in d.stored_name


def test_large_body_blocked_outside_upload(app):
    r = app.test_client().post("/contact", data={"message": "x" * 70000})
    assert r.status_code == 413


def test_delete_removes_file(app, admin_client):
    did = make_doc(app, "admin")
    with app.app_context():
        import os
        path = os.path.join(app.config["DOCUMENTS_FOLDER"], db.session.get(Document, did).stored_name)
    assert os.path.exists(path)
    admin_client.post(f"/admin/documents/{did}/delete")
    assert not os.path.exists(path)


# --- Admin client management -------------------------------------------------

def test_admin_creates_client_and_gets_link(app, admin_client):
    r = admin_client.post("/admin/clients/new", data={"name": "Carol", "email": "Carol@Example.com", "organisation": "Carol Ltd"})
    assert r.status_code == 200 and b"/account/setup/" in r.data
    with app.app_context():
        u = User.query.filter_by(email="carol@example.com").one()
        assert u.role == "client" and u.password_hash is None


def test_cannot_escalate_role_via_form(app, admin_client):
    admin_client.post("/admin/clients/new", data={"name": "Eve", "email": "eve@example.com", "role": "admin"})
    with app.app_context():
        assert User.query.filter_by(email="eve@example.com").one().role == "client"


def test_private_pages_not_cached_or_indexed(app, admin_client):
    r = admin_client.get("/admin/")
    assert r.headers["Cache-Control"] == "no-store" and "noindex" in r.headers["X-Robots-Tag"]


def test_seed_import_is_admin_only(app, tmp_path):
    seed = tmp_path / "seed"
    seed.mkdir()
    (seed / "Guide.pdf").write_bytes(pdf_bytes())
    out = app.test_cli_runner().invoke(args=["import-seed-documents", "--folder", str(seed)])
    assert "Imported 1" in out.output
    with app.app_context():
        assert Document.query.one().visibility == "admin"
    assert "Imported 0" in app.test_cli_runner().invoke(args=["import-seed-documents", "--folder", str(seed)]).output


# --- Admin from secrets, and the profile page --------------------------------

def test_ensure_admin_creates_once_and_never_overwrites(app, monkeypatch):
    runner = app.test_cli_runner()
    monkeypatch.setenv("ADMIN_EMAIL", "Owner@Example.com")
    monkeypatch.setenv("ADMIN_PASSWORD", "too short")
    r = runner.invoke(args=["ensure-admin"])
    assert r.exit_code != 0 and "not accepted" in r.output
    monkeypatch.setenv("ADMIN_PASSWORD", "blue river lamp morning")
    monkeypatch.setenv("ADMIN_NAME", "Martin")
    r = runner.invoke(args=["ensure-admin"])
    assert r.exit_code == 0, r.output
    with app.app_context():
        u = User.query.filter_by(email="owner@example.com").one()
        assert u.is_admin and u.name == "Martin"
        first_hash = u.password_hash
    monkeypatch.setenv("ADMIN_PASSWORD", "a different long passphrase")
    r = runner.invoke(args=["ensure-admin"])
    assert "already exists" in r.output
    with app.app_context():
        assert User.query.filter_by(email="owner@example.com").one().password_hash == first_hash
    c = app.test_client()
    assert login(c, "owner@example.com", "blue river lamp morning").status_code == 302


def test_ensure_admin_skips_without_secrets(app, monkeypatch):
    monkeypatch.delenv("ADMIN_EMAIL", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    r = app.test_cli_runner().invoke(args=["ensure-admin"])
    assert r.exit_code == 0 and "skipping" in r.output


def test_profile_updates_name_only_for_self(app):
    c = app.test_client()
    assert c.get("/account/profile").status_code == 302          # signed out -> login
    login(c, "alice@client.test")
    assert c.get("/account/profile").status_code == 200
    r = c.post("/account/profile", data={"name": "Alice Wanjiru", "organisation": "Wanjiru Stores", "email": "evil@x.com", "role": "admin"})
    assert r.status_code == 302
    with app.app_context():
        u = db.session.get(User, app.ids["alice"])
        assert (u.name, u.organisation, u.email, u.role) == ("Alice Wanjiru", "Wanjiru Stores", "alice@client.test", "client")
    assert c.post("/account/profile", data={"name": ""}).status_code == 200   # validation error, nothing saved
    assert c.post("/account/profile", data={"name": "Bad\nName"}).status_code == 200


def test_seed_import_adds_once_and_replaces_changed_versions(app, tmp_path):
    seed = tmp_path / "seed"; seed.mkdir()
    (seed / "Apex_Solutions_Hosting_Agreement.pdf").write_bytes(pdf_bytes())
    (seed / "notes.txt").write_text("ignored")
    runner = app.test_cli_runner()
    assert "Imported 1 new" in runner.invoke(args=["import-seed-documents", "--folder", str(seed)]).output
    assert "Imported 0 new and updated 0" in runner.invoke(args=["import-seed-documents", "--folder", str(seed)]).output
    with app.app_context():
        doc = Document.query.one()
        assert (doc.visibility, doc.category) == ("admin", "Agreements")
        doc.visibility = "clients"; db.session.commit()
    (seed / "Apex_Solutions_Hosting_Agreement.pdf").write_bytes(pdf_bytes() + b"% v2\n")
    assert "updated 1" in runner.invoke(args=["import-seed-documents", "--folder", str(seed)]).output
    with app.app_context():
        doc = Document.query.one()
        assert doc.visibility == "clients"        # sharing kept
        assert doc.size == len(pdf_bytes() + b"% v2\n")
