from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import ClassDefinition, Playthrough
from app.services.gameplay import create_soldier

bp = Blueprint("soldiers", __name__, url_prefix="/soldiers")
@bp.get("")
@login_required
def index():
    playthrough = Playthrough.query.filter_by(owner_id=current_user.id, archived=False).first_or_404(); classes = ClassDefinition.query.filter(ClassDefinition.content_pack_id.in_([p.id for p in playthrough.content_packs])).all(); return render_template("soldiers/index.html", playthrough=playthrough, classes=classes)
@bp.post("/create")
@login_required
def create():
    playthrough = Playthrough.query.filter_by(id=request.form["playthrough_id"], owner_id=current_user.id).first_or_404(); create_soldier(playthrough, request.form.get("class_definition_id", type=int) or None, request.form.get("rank", "Rookie"), first_name=request.form.get("first_name", ""), last_name=request.form.get("last_name", ""), nickname=request.form.get("nickname", ""), status=request.form.get("status", "Available"), notes=request.form.get("notes", "")); return redirect(url_for("soldiers.index"))
