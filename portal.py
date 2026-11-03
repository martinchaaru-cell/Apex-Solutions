"""Client portal, and the single checked route that serves every document download (B3, B8)."""
import os

from flask import Blueprint, abort, g, render_template, send_file

from extensions import db
from models import Document
from security import audit, login_required, role_required
from storage import path_for

bp = Blueprint("portal", __name__)


def documents_for(user):
    """Documents a client may see: shared with all clients, or with this client."""
    return (Document.query
            .filter((Document.visibility == "clients") |
                    ((Document.visibility == "client") & (Document.client_id == user.id)))
            .order_by(Document.category, Document.title).all())


@bp.route("/portal/")
@role_required("client")
def dashboard():
    docs = documents_for(g.user)
    grouped = {}
    for d in docs:
        grouped.setdefault(d.category, []).append(d)
    return render_template("portal/dashboard.html", grouped=grouped, count=len(docs))


@bp.route("/documents/<did>/download")
@login_required
def download(did):
    doc = db.session.get(Document, did)
    # Same 404 whether the document is missing or belongs to someone else, so IDs reveal nothing (B3).
    if doc is None or not doc.visible_to(g.user):
        if doc is not None:
            audit("download_denied", did)
        abort(404)
    try:
        path = path_for(doc)
    except FileNotFoundError:
        abort(404)
    if not os.path.isfile(path):
        abort(404)
    audit("document_downloaded", doc.id)
    resp = send_file(path, mimetype=doc.mimetype, as_attachment=True, download_name=doc.original_name, max_age=0)
    resp.headers["Cache-Control"] = "no-store"
    return resp
