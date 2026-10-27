from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import CatalogueObject, Playthrough
from app.services.research import (
    ResearchCycleError,
    add_to_queue,
    prerequisites_for,
    remove_from_queue,
    reorder_queue,
    set_state,
    state_for,
    unlocks_for,
)

bp = Blueprint("research", __name__, url_prefix="/research")
def selected(): return Playthrough.query.filter_by(id=request.args.get("playthrough_id", type=int) or request.form.get("playthrough_id", type=int), owner_id=current_user.id).first() or Playthrough.query.filter_by(owner_id=current_user.id, archived=False).first_or_404()
@bp.get("")
@login_required
def index():
    playthrough = selected(); pack_ids = [pack.id for pack in playthrough.content_packs]; nodes = CatalogueObject.query.filter(CatalogueObject.content_pack_id.in_(pack_ids), CatalogueObject.object_type.in_(["research", "autopsy", "shadow_project", "proving_ground_project", "technology"])).all(); queue = sorted(playthrough.research_queue, key=lambda item: item.position); return render_template("research/index.html", playthrough=playthrough, nodes=nodes, queue=queue, focus=request.args.get("focus", type=int))
@bp.get("/graph/<int:object_id>")
@login_required
def graph(object_id):
    playthrough = selected(); direction = request.args.get("direction", "backward")
    try: result = prerequisites_for(playthrough, object_id) if direction == "backward" else unlocks_for(playthrough, object_id)
    except ResearchCycleError as error: return jsonify({"error": str(error), "cycle": [node.id for node in error.path]}), 422
    states = {node.id: state_for(playthrough, node.id) for node in result["nodes"]}; return jsonify({"nodes": [{"id": node.id, "name": node.name, "type": node.object_type, "state": states[node.id]} for node in result["nodes"]], "edges": [{"source": source, "target": target} for source, target in result["edges"]], "selected": object_id})
@bp.post("/queue/add/<int:object_id>")
@login_required
def queue_add(object_id): add_to_queue(selected(), object_id); return redirect(url_for("research.index"))
@bp.post("/queue/remove/<int:object_id>")
@login_required
def queue_remove(object_id): remove_from_queue(selected(), object_id); return redirect(url_for("research.index"))
@bp.post("/queue/reorder")
@login_required
def queue_reorder(): reorder_queue(selected(), [int(value) for value in request.form.getlist("object_ids")]); return redirect(url_for("research.index"))
@bp.post("/state/<int:object_id>")
@login_required
def state(object_id): set_state(selected(), object_id, request.form["state"]); return redirect(url_for("research.index"))
