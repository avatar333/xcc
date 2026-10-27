from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required

from app import db
from app.models import Asset, CatalogueObject, ContentPack

bp = Blueprint("catalogue", __name__, url_prefix="/catalogue")
ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}
@bp.get("/media/<path:filename>")
def media(filename): return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
@bp.get("")
@login_required
def index(): return render_template("catalogue/index.html", objects=CatalogueObject.query.filter_by(enabled=True).all())
@bp.post("/create")
@login_required
def create():
    pack = ContentPack.query.filter_by(owner_id=current_user.id, slug=f"custom-{current_user.id}").first()
    if not pack:
        pack = ContentPack(slug=f"custom-{current_user.id}", name=f"Custom content ({current_user.username})", owner=current_user); db.session.add(pack); db.session.flush()
    obj = CatalogueObject(content_pack=pack, external_key=uuid4().hex, object_type=request.form["object_type"], name=request.form["name"], description=request.form.get("description", ""), notes=request.form.get("notes", ""), source=request.form.get("source", ""), canonical=False); db.session.add(obj); db.session.flush()
    upload = request.files.get("image")
    if upload and upload.filename:
        ext = Path(upload.filename).suffix.lower().lstrip(".")
        if ext not in ALLOWED: flash("Unsupported image type.", "danger"); db.session.rollback(); return redirect(url_for("catalogue.index"))
        filename = f"{uuid4().hex}.{ext}"; upload.save(Path(current_app.config["UPLOAD_FOLDER"]) / filename); db.session.add(Asset(catalogue_object=obj, path=filename, role="icon", primary=True, alt_text=obj.name))
    db.session.commit(); return redirect(url_for("catalogue.index"))
