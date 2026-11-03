"""Site tests. These are the Level 1 evidence for the Apex Security Baseline (see security/LEVEL1_CHECKLIST.md)."""
import re

import pytest

import content as c
from app import _neutralise, create_app
from config import TestConfig
from extensions import db, limiter
from models import Enquiry

PAGES = (
    ["/", "/solutions", "/industries", "/how-we-work", "/trust-security", "/our-work", "/pricing", "/about",
     "/contact", "/privacy", "/terms"]
    + [f"/solutions/{k}" for k in c.SOLUTION_ORDER]
    + [f"/industries/{k}" for k in c.INDUSTRIES]
    + [f"/our-work/{w['slug']}" for w in c.WORK]
)

VALID = {
    "name": "Wanjiku Test",
    "email": "wanjiku@example.com",
    "phone": "+254 700 000 000",
    "organisation": "Test Shop",
    "service": "pos-systems",
    "budget": "150k-300k",
    "message": "We need a POS for two tills with M-Pesa and stock control.",
    "consent": "y",
}


class NoCsrf(TestConfig):
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    app = create_app(NoCsrf)
    limiter.reset()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def count(app):
    with app.app_context():
        return Enquiry.query.count()


# --- Pages ---------------------------------------------------------------

@pytest.mark.parametrize("path", PAGES)
def test_page_renders(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert b"<h1" in r.data


def test_unknown_page_is_generic_404(client):
    r = client.get("/solutions/does-not-exist")
    assert r.status_code == 404
    assert b"Page not found" in r.data
    assert b"Traceback" not in r.data


@pytest.mark.parametrize("path", ["/.env", "/.git/config", "/console", "/debug", "/backup.sql"])
def test_sensitive_paths_not_exposed(client, path):  # G3, D7
    assert client.get(path).status_code == 404


def test_sitemap_lists_every_page(client):
    xml = client.get("/sitemap.xml").get_data(as_text=True)
    for p in PAGES:
        assert f"{p}</loc>" in xml


# --- Headers (G1, G7, E6) ------------------------------------------------

@pytest.mark.parametrize("path", ["/", "/contact", "/missing-page"])
def test_security_headers(client, path):
    h = client.get(path).headers
    csp = h["Content-Security-Policy"]
    assert "default-src 'self'" in csp and "frame-ancestors 'none'" in csp
    assert "unsafe-inline" not in csp and "unsafe-eval" not in csp
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["X-Frame-Options"] == "DENY"
    assert h["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in h["Permissions-Policy"]


def test_contact_page_not_cached(client):
    assert client.get("/contact").headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize("path", PAGES)
def test_no_inline_script_or_style(client, path):
    """The strict CSP blocks inline code, so none may exist."""
    html = client.get(path).get_data(as_text=True)
    assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html)
    assert " style=" not in html and "<style" not in html
    assert not re.search(r"\son[a-z]+=", html)


# --- Copy rules (BUILD_SPEC section 2) -----------------------------------

BANNED = [
    r"ISO\s*27001", r"PCI[\s-]*DSS", r"GDPR", r"SOC\s*2", r"certified", r"unhackable",
    r"100\s*%", r"bank-grade", r"enterprise-grade", r"military-grade", r"24/7",
    r"\d+\+\s*(projects|clients)", r"client satisfaction", r"guarantee",
]


@pytest.mark.parametrize("path", PAGES)
def test_no_banned_claims(client, path):
    text = re.sub(r"<[^>]+>", " ", client.get(path).get_data(as_text=True))
    for pattern in BANNED:
        hits = re.findall(pattern, text, flags=re.I)
        # "certified partner" is the honest description of who does penetration tests.
        hits = [h for h in hits if not (h.lower() == "certified" and "certified partner" in text.lower())]
        assert not hits, f"{path}: banned claim {pattern!r}"


def test_contact_details_hidden_when_unset(client):
    html = client.get("/contact").get_data(as_text=True)
    assert "mailto:" not in html and "wa.me" not in html and "tel:" not in html


def test_contact_details_shown_when_set():
    class Cfg(NoCsrf):
        CONTACT_EMAIL = "hello@apex.example"
        WHATSAPP_NUMBER = "254700000000"
    html = create_app(Cfg).test_client().get("/contact").get_data(as_text=True)
    assert "mailto:hello@apex.example" in html and "https://wa.me/254700000000" in html


def test_prices_state_vat(client):
    for path in ["/pricing"] + [f"/solutions/{k}" for k in c.SOLUTION_ORDER]:
        assert "excl" in client.get(path).get_data(as_text=True)


# --- Contact form --------------------------------------------------------

def test_valid_enquiry_is_stored_and_redirects(app, client):
    r = client.post("/contact", data=VALID)
    assert r.status_code == 302 and r.headers["Location"].endswith("/contact/thanks")
    with app.app_context():
        e = Enquiry.query.one()
        assert e.email == "wanjiku@example.com" and e.service == "pos-systems"
        assert len(e.id) == 36  # UUID, not a sequential id (B9)


def test_honeypot_stores_nothing(app, client):
    r = client.post("/contact", data={**VALID, "website": "http://spam.example"})
    assert r.status_code == 302
    assert count(app) == 0


@pytest.mark.parametrize("field,value", [
    ("email", "not-an-email"),
    ("name", "A"),
    ("name", "Line one\r\nBcc: victim@example.com"),
    ("message", "too short"),
    ("message", "x" * 3001),
    ("service", "admin"),
    ("budget", "1000000000"),
    ("phone", "<script>"),
    ("consent", ""),
    ("message", "null byte \x00 in the middle of a long enough message"),
])
def test_invalid_input_rejected(app, client, field, value):  # C2, G8
    data = {**VALID, field: value}
    if value == "":
        data.pop(field)
    r = client.post("/contact", data=data)
    assert r.status_code == 422
    assert count(app) == 0


def test_xss_is_escaped(client):  # C3
    r = client.post("/contact", data={**VALID, "name": "<script>alert(1)</script>", "email": "bad"})
    html = r.get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_mass_assignment_ignored(app, client):  # B5
    client.post("/contact", data={**VALID, "status": "won", "id": "1"})
    with app.app_context():
        e = Enquiry.query.one()
        assert e.status == "new" and e.id != "1"


def test_csrf_required():  # C4
    app = create_app(TestConfig)
    limiter.reset()
    r = app.test_client().post("/contact", data=VALID)
    assert r.status_code == 400
    assert b"Form expired" in r.data


def test_rate_limit_on_post(app, client):  # F2
    codes = [client.post("/contact", data=VALID).status_code for _ in range(6)]
    assert codes[:5] == [302] * 5 and codes[5] == 429
    assert client.get("/contact").status_code == 200  # browsing is never blocked


def test_oversized_body_rejected(client):
    assert client.post("/contact", data={**VALID, "message": "x" * 70000}).status_code == 413


def test_notification_uses_fixed_headers(app, monkeypatch):  # G8
    sent = {}

    class FakeSMTP:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def starttls(self, context): sent["tls"] = context is not None
        def login(self, *a): pass
        def send_message(self, msg): sent["msg"] = msg

    import mail
    monkeypatch.setattr(mail.smtplib, "SMTP", FakeSMTP)
    app.config.update(SMTP_HOST="smtp.example", MAIL_FROM="web@apex.example", MAIL_TO="sales@apex.example")
    client = app.test_client()
    client.post("/contact", data={**VALID, "email": "evil@example.com"})
    msg = sent["msg"]
    assert msg["From"] == "web@apex.example" and msg["To"] == "sales@apex.example"
    assert msg["Subject"] == "New website enquiry" and sent["tls"]


# --- Operations ----------------------------------------------------------

def test_export_neutralises_formulas():  # C11
    assert _neutralise("=HYPERLINK(\"http://x\")").startswith("'")
    assert _neutralise("+254700") == "'+254700"
    assert _neutralise("@cmd") == "'@cmd"
    assert _neutralise("Normal text") == "Normal text"


def test_export_and_delete_commands(app, client, tmp_path):  # C11, E8
    client.post("/contact", data={**VALID, "organisation": "=cmd|' /C calc'!A0"})
    out = tmp_path / "e.csv"
    runner = app.test_cli_runner()
    assert "Exported 1" in runner.invoke(args=["export-enquiries", str(out)]).output
    assert "'=cmd" in out.read_text()
    assert "Deleted 1" in runner.invoke(args=["delete-enquiry", "WANJIKU@example.com"]).output
    assert count(app) == 0


def test_refuses_to_start_without_strong_secret():  # D6
    class Weak(TestConfig):
        SECRET_KEY = "short"
    with pytest.raises(RuntimeError):
        create_app(Weak)


def test_debug_is_off(app):  # D7
    assert not app.debug


# --- Replit preview mode -------------------------------------------------

def test_preview_mode_allows_only_replit_framing():
    class Preview(NoCsrf):
        PREVIEW_MODE = True
    h = create_app(Preview).test_client().get("/").headers
    assert "frame-ancestors https://replit.com" in h["Content-Security-Policy"]
    assert "frame-ancestors *" not in h["Content-Security-Policy"]
    assert "X-Frame-Options" not in h


def test_framing_blocked_by_default(client):
    h = client.get("/").headers
    assert "frame-ancestors 'none'" in h["Content-Security-Policy"] and h["X-Frame-Options"] == "DENY"


def test_preview_mode_off_unless_set(monkeypatch):
    import importlib
    import config as cfg
    monkeypatch.delenv("PREVIEW_MODE", raising=False)
    importlib.reload(cfg)
    assert cfg.Config.PREVIEW_MODE is False and cfg.Config.SESSION_COOKIE_SAMESITE == "Lax"


# --- Catalogue completeness (Service Guide v1.1, section 3 and 6.4) --------

GUIDE_PRICES = [
    "15,000 – 40,000", "50,000 – 120,000", "80,000 – 200,000", "100,000 – 300,000", "150,000 – 500,000",
    "200,000 – 600,000", "300,000 – 800,000", "80,000 – 250,000", "120,000 – 350,000", "150,000 – 400,000",
    "100,000 – 250,000", "250,000 – 800,000", "60,000 – 200,000", "100,000 – 350,000", "50,000 – 250,000",
    "30,000 – 150,000", "30,000 – 80,000", "30,000 – 100,000", "20,000 – 70,000", "20,000 – 100,000",
    "25,000 – 100,000", "10,000 – 50,000", "Quoted by the partner", "3,000 – 6,000 per hour",
    "500 – 1,000", "2,500 – 5,000", "6,000 – 12,000", "18,000 – 35,000",
    "5,000", "10,000 – 15,000", "15,000 – 22,000", "25,000 and above",
]


def test_pricing_page_lists_every_guide_price(client):
    html = client.get("/pricing").get_data(as_text=True)
    missing = [p for p in GUIDE_PRICES if p not in html]
    assert not missing, f"missing from /pricing: {missing}"


def test_every_catalogue_category_has_a_page(client):
    for slug in c.SOLUTION_ORDER:
        assert client.get(f"/solutions/{slug}").status_code == 200
    assert len(c.SOLUTION_ORDER) == 8


# --- Detailed service descriptions -------------------------------------------

import service_details  # noqa: E402

SERVICE_FIELDS = ("slug", "icon", "availability", "name", "what", "uses", "can", "example", "price", "timeline")


def test_every_solution_has_detailed_services():
    import content
    assert set(service_details.DETAILS) == set(content.SOLUTION_ORDER)
    seen = set()
    for area, services in service_details.DETAILS.items():
        assert len(services) >= 3, area
        for v in services:
            for f in SERVICE_FIELDS:
                assert v.get(f), f"{area}/{v.get('slug')} missing {f}"
            assert len(v["uses"]) >= 2 and len(v["can"]) >= 3, v["slug"]
            assert len(v["what"]) > 80, v["slug"]
            assert v["availability"] in (content.NOW, content.CONSULT, content.SPECIALIST)
            assert v["slug"] not in seen, f"duplicate service slug {v['slug']}"
            seen.add(v["slug"])


def test_service_explorer_renders_every_service(client):
    for area, services in service_details.DETAILS.items():
        html = client.get(f"/solutions/{area}").get_data(as_text=True)
        assert 'data-svx' in html
        for v in services:
            assert f'id="{v["slug"]}"' in html
            assert f'href="#{v["slug"]}"' in html
            assert v["example"][:40].replace("'", "&#39;") in html


def test_solutions_overview_links_to_every_service(client):
    html = client.get("/solutions").get_data(as_text=True)
    for area, services in service_details.DETAILS.items():
        for v in services:
            assert f'/solutions/{area}#{v["slug"]}' in html


def test_quote_link_prefills_service(client):
    html = client.get("/contact?service=pos-systems&item=retail-pos").get_data(as_text=True)
    assert "I am interested in: Retail POS." in html
    html = client.get("/contact?service=pos-systems&item=<script>").get_data(as_text=True)
    assert "I am interested in" not in html


def test_database_url_from_hosting_provider_is_normalised(monkeypatch):
    import importlib, config
    for given in ("postgres://u:p@h/db", "postgresql://u:p@h/db"):
        monkeypatch.setenv("DATABASE_URL", given)
        importlib.reload(config)
        assert config.Config.SQLALCHEMY_DATABASE_URI == "postgresql+psycopg://u:p@h/db"
    monkeypatch.delenv("DATABASE_URL")
    importlib.reload(config)
