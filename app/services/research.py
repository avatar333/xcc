from app import db
from app.models import (
    CatalogueObject,
    PlaythroughObjectState,
    ResearchPrerequisite,
    ResearchQueueItem,
    ResearchUnlock,
)

STATES = {"Unknown", "Available", "Planned", "In Progress", "Completed", "Unlocked", "Acquired"}

class ResearchCycleError(ValueError):
    def __init__(self, path):
        self.path = path
        super().__init__("Research dependency cycle detected: " + " → ".join(node.name for node in path))

def _allowed_ids(playthrough):
    return {obj.id for pack in playthrough.content_packs for obj in pack.objects}

def _walk(playthrough, start_id, reverse):
    allowed = _allowed_ids(playthrough); nodes = {}; edges = []; visiting = []; visited = set()
    def visit(current):
        if current not in allowed: return
        if current in visiting:
            cycle_start = visiting.index(current); raise ResearchCycleError([db.session.get(CatalogueObject, item) for item in visiting[cycle_start:]] + [db.session.get(CatalogueObject, current)])
        if current in visited: return
        visiting.append(current); node = db.session.get(CatalogueObject, current); nodes[current] = node
        relations = ResearchPrerequisite.query.filter_by(node_id=current).all() if reverse else ResearchUnlock.query.filter_by(research_id=current).all()
        next_ids = [relation.prerequisite_id for relation in relations] if reverse else [relation.unlocked_id for relation in relations]
        for next_id in next_ids:
            if next_id in allowed: edges.append((next_id, current) if reverse else (current, next_id)); visit(next_id)
        visiting.pop(); visited.add(current)
    visit(start_id)
    return {"nodes": list(nodes.values()), "edges": edges, "cycle": False}

def prerequisites_for(playthrough, object_id): return _walk(playthrough, object_id, True)
def unlocks_for(playthrough, object_id): return _walk(playthrough, object_id, False)

def state_for(playthrough, object_id):
    state = PlaythroughObjectState.query.filter_by(playthrough_id=playthrough.id, object_id=object_id).first()
    return state.state if state else "Unknown"

def set_state(playthrough, object_id, state):
    if state not in STATES: raise ValueError("Unknown research state")
    record = PlaythroughObjectState.query.filter_by(playthrough_id=playthrough.id, object_id=object_id).first() or PlaythroughObjectState(playthrough=playthrough, object_id=object_id)
    record.state = state; db.session.add(record); db.session.commit(); return record

def add_to_queue(playthrough, object_id):
    if object_id not in _allowed_ids(playthrough): raise ValueError("Research is not available in this playthrough")
    item = ResearchQueueItem.query.filter_by(playthrough_id=playthrough.id, object_id=object_id).first()
    if not item:
        position = (db.session.query(db.func.max(ResearchQueueItem.position)).filter_by(playthrough_id=playthrough.id).scalar() or 0) + 1
        item = ResearchQueueItem(playthrough=playthrough, object_id=object_id, position=position); db.session.add(item); db.session.commit()
    return item

def remove_from_queue(playthrough, object_id):
    item = ResearchQueueItem.query.filter_by(playthrough_id=playthrough.id, object_id=object_id).first()
    if item: db.session.delete(item); db.session.commit()

def reorder_queue(playthrough, ordered_ids):
    items = {item.object_id: item for item in ResearchQueueItem.query.filter_by(playthrough_id=playthrough.id).all()}
    for position, object_id in enumerate(ordered_ids, 1):
        if object_id in items: items[object_id].position = position
    db.session.commit()
