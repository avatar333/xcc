from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import CatalogueObject, EquipmentBuild, Playthrough, Soldier
from app.services.equipment import clone_build
from app.services.gameplay import visible_catalogue

bp = Blueprint("equipment", __name__, url_prefix="/equipment")
@bp.get("")
@login_required
def index():
    playthrough = Playthrough.query.filter_by(owner_id=current_user.id, archived=False).first_or_404(); return render_template("equipment/index.html", playthrough=playthrough, builds=playthrough.equipment_builds, weapons=visible_catalogue(playthrough, "weapon"), armour=visible_catalogue(playthrough, "armour"))
@bp.post("/create")
@login_required
def create():
    playthrough = Playthrough.query.filter_by(id=request.form["playthrough_id"], owner_id=current_user.id).first_or_404(); base = CatalogueObject.query.get_or_404(request.form["base_item_id"], description="Base item not found")
    if base.content_pack not in playthrough.content_packs: return "Item is not available", 400
    db.session.add(EquipmentBuild(owner=current_user, playthrough=playthrough, name=request.form["name"], build_type=request.form["build_type"], base_item=base, purpose=request.form.get("purpose", ""), notes=request.form.get("notes", ""))); db.session.commit(); return redirect(url_for("equipment.index"))
@bp.post("/<int:build_id>/clone")
@login_required
def clone(build_id):
    build = EquipmentBuild.query.filter_by(id=build_id, owner_id=current_user.id).first_or_404(); clone_build(build, current_user, build.playthrough); return redirect(url_for("equipment.index"))
@bp.post("/<int:build_id>/assign/<int:soldier_id>")
@login_required
def assign(build_id, soldier_id):
    build = EquipmentBuild.query.filter_by(id=build_id, owner_id=current_user.id).first_or_404(); soldier = Soldier.query.filter_by(id=soldier_id, playthrough_id=build.playthrough_id).first_or_404(); setattr(soldier, "weapon_build_id" if build.build_type == "Weapon" else "armour_build_id", build.id); db.session.commit(); return redirect(url_for("equipment.index"))
