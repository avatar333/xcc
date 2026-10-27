from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.models import Playthrough
from app.services.gameplay import ensure_avenger_rooms, set_room, visible_catalogue

bp = Blueprint("avenger", __name__, url_prefix="/avenger")
def selected_playthrough(): return Playthrough.query.filter_by(id=request.args.get("playthrough_id", type=int) or request.form.get("playthrough_id", type=int) or session.get("active_playthrough_id"), owner_id=current_user.id).first() or Playthrough.query.filter_by(owner_id=current_user.id, archived=False).first_or_404()
@bp.get("")
@login_required
def index():
    playthrough = selected_playthrough(); ensure_avenger_rooms(playthrough); return render_template("avenger/index.html", playthrough=playthrough, rooms=playthrough.avenger_rooms, facilities=visible_catalogue(playthrough, "facility"))
@bp.post("/room/<int:room_id>")
@login_required
def update(room_id):
    playthrough = selected_playthrough(); set_room(playthrough, room_id, request.form.get("facility_id"), request.form.get("planned_facility_id"), request.form.get("room_state"), request.form.get("planning_status")); return redirect(url_for("avenger.index", playthrough_id=playthrough.id))
