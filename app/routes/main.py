from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import Playthrough

bp = Blueprint("main", __name__)
@bp.get("/")
def index(): return render_template("landing.html")
@bp.get("/dashboard")
@login_required
def dashboard():
    playthrough = Playthrough.query.filter_by(owner_id=current_user.id, archived=False).first()
    if not playthrough: return render_template("dashboard.html", playthrough=None)
    return render_template("dashboard.html", playthrough=playthrough, soldiers=playthrough.soldiers, builds=playthrough.equipment_builds, queue=sorted(playthrough.research_queue, key=lambda item: item.position), rooms=playthrough.avenger_rooms)
