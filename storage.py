"""Document uploads (Security Baseline C5, B8).

Files are checked by extension AND content, renamed to a random name, and stored in a
private folder outside the web root. They are only ever sent back as downloads.
"""
import hashlib
import io
import os
import re
import uuid
import zipfile

from flask import current_app

# extension -> (mimetype, check function name)
ALLOWED = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}
_OOXML_PART = {"docx": "word/document.xml", "xlsx": "xl/workbook.xml", "pptx": "ppt/presentation.xml"}


class UploadError(ValueError):
    """A plain-language reason the file was refused."""


def folder():
    path = current_app.config["DOCUMENTS_FOLDER"]
    os.makedirs(path, mode=0o700, exist_ok=True)
    return path


def _content_ok(ext, data):
    if ext == "pdf":
        return data[:5] == b"%PDF-"
    if data[:4] != b"PK\x03\x04":
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = set(z.namelist())
            if len(names) > 5000:            # zip-bomb guard
                return False
            total = sum(i.file_size for i in z.infolist())
            if total > 200 * 1024 * 1024:
                return False
            if any(n.lower().endswith((".exe", ".js", ".vbs", ".bat", ".cmd", ".ps1")) for n in names):
                return False
            if "[Content_Types].xml" not in names or _OOXML_PART[ext] not in names:
                return False
            # Macro-enabled content is not accepted, even with a normal extension.
            return not any(n.lower().endswith("vbaproject.bin") for n in names)
    except zipfile.BadZipFile:
        return False


def safe_display_name(name):
    """A tidy filename for the download, with no path parts or unusual characters."""
    base = os.path.basename(name or "").strip()
    stem, dot, ext = base.rpartition(".")
    stem = re.sub(r"[^A-Za-z0-9 ._()-]+", "_", stem or ext)[:150].strip(" .") or "document"
    return f"{stem}.{ext.lower()}" if dot else stem


def check_and_store(file_storage):
    """Validate an uploaded file and save it. Returns a dict for the Document row."""
    if not file_storage or not file_storage.filename:
        raise UploadError("Choose a file to upload.")
    original = safe_display_name(file_storage.filename)
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if ext not in ALLOWED:
        raise UploadError("Only PDF, Word (.docx), Excel (.xlsx) and PowerPoint (.pptx) files can be uploaded.")
    limit = current_app.config["MAX_DOCUMENT_MB"] * 1024 * 1024
    data = file_storage.read(limit + 1)
    if len(data) > limit:
        raise UploadError(f"That file is larger than {current_app.config['MAX_DOCUMENT_MB']} MB.")
    if not data:
        raise UploadError("That file is empty.")
    if not _content_ok(ext, data):
        raise UploadError(f"That file's contents do not match a .{ext} document, or it contains macros. Save it again as a normal .{ext} and retry.")
    stored = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(folder(), stored)
    with open(path, "xb") as f:      # never overwrite
        f.write(data)
    os.chmod(path, 0o600)
    return {
        "original_name": original, "stored_name": stored, "extension": ext,
        "mimetype": ALLOWED[ext], "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
    }


def path_for(doc):
    """Full path of a stored document, confined to the documents folder (C9)."""
    base = os.path.realpath(folder())
    path = os.path.realpath(os.path.join(base, doc.stored_name))
    if not path.startswith(base + os.sep):
        raise FileNotFoundError(doc.stored_name)
    return path


def delete_file(doc):
    try:
        os.remove(path_for(doc))
    except FileNotFoundError:
        pass


def human_size(n):
    for unit in ("bytes", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n:,.0f} {unit}" if unit == "bytes" else f"{n:,.1f} {unit}"
        n /= 1024
