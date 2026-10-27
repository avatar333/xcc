from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app import db
from app.models import ContentPack, Playthrough
from app.services.seed import validate_pack_dependencies

bp = Blueprint("playthroughs", __name__, url_prefix="/playthroughs")
@bp.get("")
@login_required
def index(): return render_template("playthroughs/index.html", playthroughs=current_user.playthroughs, packs=ContentPack.query.filter_by(enabled=True).all())
@bp.post("/create")
@login_required
def create():
    p = Playthrough(owner=current_user, name=request.form.get("name", "Untitled").strip(), description=request.form.get("description", ""))
    db.session.add(p)
    ids = request.form.getlist("pack_ids"); p.content_packs = ContentPack.query.filter(ContentPack.id.in_(ids)).all() if ids else []
    if not validate_pack_dependencies(p.content_packs):
        db.session.rollback(); flash("Selected content packs require their parent packs.", "danger"); return redirect(url_for("playthroughs.index"))
    db.session.commit(); return redirect(url_for("playthroughs.index"))
@bp.post("/<int:playthrough_id>/edit")
@login_required
def edit(playthrough_id):
    p = Playthrough.query.filter_by(id=playthrough_id, owner_id=current_user.id).first_or_404(); p.name = request.form.get("name", p.name).strip(); p.description = request.form.get("description", p.description); db.session.commit(); return redirect(url_for("playthroughs.index"))
@bp.post("/<int:playthrough_id>/select")
@login_required
def select(playthrough_id):
    Playthrough.query.filter_by(id=playthrough_id, owner_id=current_user.id).first_or_404(); session["active_playthrough_id"] = playthrough_id; return redirect(request.referrer or url_for("main.dashboard"))
@bp.post("/<int:playthrough_id>/archive")
@login_required
def archive(playthrough_id):
    p = Playthrough.query.filter_by(id=playthrough_id, owner_id=current_user.id).first_or_404(); p.archived = True; db.session.commit(); return redirect(url_for("playthroughs.index"))
