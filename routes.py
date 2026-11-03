"""Public routes. Every page is deliberately public; there is no login (Level 1)."""
import logging
import os
from datetime import date

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from flask import Response

import content as c
import service_details
from extensions import db, limiter
from forms import ContactForm
from mail import notify_new_enquiry
from models import Enquiry

service_details.attach(c.SOLUTIONS)

bp = Blueprint("site", __name__)
log = logging.getLogger(__name__)

WORK_BY_SLUG = {w["slug"]: w for w in c.WORK}


def work_image(slug):
    """Return the static path of a real screenshot for a project, if one has been added."""
    folder = os.path.join(current_app.static_folder, "img", "work")
    for ext in ("webp", "png", "jpg"):
        name = f"{slug}.{ext}"
        if os.path.isfile(os.path.join(folder, name)):
            return f"img/work/{name}"
    return None


@bp.app_template_filter("slug")
def slug_filter(text):
    """'NGOs & Institutions' -> 'ngos-institutions' (used for page anchors)."""
    import re
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


@bp.app_context_processor
def inject_globals():
    cfg = current_app.config
    return {
        "c": c,
        "nav_solutions": [c.SOLUTIONS[s] for s in c.SOLUTION_ORDER],
        "nav_industries": list(c.INDUSTRIES.values()),
        "contact": {
            "email": cfg["CONTACT_EMAIL"],
            "phone": cfg["CONTACT_PHONE"],
            "whatsapp": cfg["WHATSAPP_NUMBER"],
            "location": cfg["LOCATION_TEXT"],
        },
        "site_url": cfg["SITE_URL"],
        "work_image": work_image,
        "starting_price": c.starting_price,
        "year": date.today().year,
    }


@bp.route("/")
def home():
    return render_template("home.html", work=c.WORK)


@bp.route("/solutions")
def solutions():
    return render_template("solutions.html")


@bp.route("/solutions/<slug>")
def solution(slug):
    s = c.SOLUTIONS.get(slug)
    if not s:
        abort(404)
    others = [c.SOLUTIONS[k] for k in c.SOLUTION_ORDER if k != slug]
    return render_template("solution.html", s=s, others=others)


@bp.route("/industries/<slug>")
def industry(slug):
    ind = c.INDUSTRIES.get(slug)
    if not ind:
        abort(404)
    sols = [c.SOLUTIONS[k] for k in ind["solutions"]]
    work = [WORK_BY_SLUG[k] for k in ind["work"]]
    return render_template("industry.html", ind=ind, sols=sols, work=work)


@bp.route("/industries")
def industries():
    return render_template("industries.html")


@bp.route("/trust-security")
def trust():
    return render_template("trust.html")


@bp.route("/how-we-work")
def how_we_work():
    return render_template("how_we_work.html")


@bp.route("/our-work")
def our_work():
    return render_template("work.html", work=c.WORK)


@bp.route("/our-work/<slug>")
def case_study(slug):
    w = WORK_BY_SLUG.get(slug)
    if not w:
        abort(404)
    others = [x for x in c.WORK if x["slug"] != slug]
    return render_template("case_study.html", w=w, others=others)


@bp.route("/pricing")
def pricing():
    return render_template("pricing.html")


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/contact", methods=["GET", "POST"])
@limiter.limit(lambda: current_app.config["CONTACT_RATE_LIMIT"], methods=["POST"])
def contact():
    form = ContactForm()
    preset = request.args.get("service", "")
    if request.method == "GET" and preset in dict(c.SERVICE_CHOICES):
        form.service.data = preset
        # ?item=<service slug> starts the message with the service the visitor was reading about.
        item = request.args.get("item", "")
        chosen = next((v for v in c.SOLUTIONS.get(preset, {}).get("services", []) if v["slug"] == item), None)
        if chosen and not form.message.data:
            form.message.data = f"I am interested in: {chosen['name']}.\n\n"

    if form.validate_on_submit():
        if form.website.data:  # honeypot tripped: pretend success, store nothing
            log.info("Contact honeypot triggered from %s", request.remote_addr)
            return redirect(url_for("site.contact_thanks"))
        enquiry = Enquiry(
            name=form.name.data, email=form.email.data.lower(), phone=form.phone.data or None,
            organisation=form.organisation.data or None, service=form.service.data,
            budget=form.budget.data, message=form.message.data,
        )
        db.session.add(enquiry)
        db.session.commit()
        log.info("Enquiry stored, reference %s", enquiry.id)  # no personal data in logs (J2)
        notify_new_enquiry(enquiry)
        return redirect(url_for("site.contact_thanks"))  # PRG: no resubmit on refresh

    status = 422 if request.method == "POST" else 200
    return render_template("contact.html", form=form), status


@bp.route("/contact/thanks")
def contact_thanks():
    return render_template("contact_thanks.html")


@bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@bp.route("/terms")
def terms():
    return render_template("terms.html")


@bp.route("/robots.txt")
def robots():
    private = "".join(f"Disallow: {p}\n" for p in ("/contact/thanks", "/admin", "/portal", "/account", "/login", "/documents"))
    body = f"User-agent: *\nAllow: /\n{private}Sitemap: {current_app.config['SITE_URL']}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    base = current_app.config["SITE_URL"]
    paths = ["/", "/solutions", "/industries", "/how-we-work", "/trust-security", "/our-work", "/pricing",
             "/about", "/contact", "/privacy", "/terms"]
    paths += [f"/solutions/{k}" for k in c.SOLUTION_ORDER]
    paths += [f"/industries/{k}" for k in c.INDUSTRIES]
    paths += [f"/our-work/{w['slug']}" for w in c.WORK]
    urls = "".join(f"<url><loc>{base}{p}</loc></url>" for p in paths)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, mimetype="application/xml")


@bp.route("/.well-known/security.txt")
def security_txt():  # J9
    cfg = current_app.config
    contact = cfg["SECURITY_CONTACT"] or cfg["CONTACT_EMAIL"]
    if not contact:
        abort(404)
    year = date.today().year + 1
    body = (f"Contact: mailto:{contact}\nExpires: {year}-12-31T23:59:59Z\n"
            f"Preferred-Languages: en\nCanonical: {cfg['SITE_URL']}/.well-known/security.txt\n")
    return Response(body, mimetype="text/plain")
