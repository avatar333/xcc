from app import db
from app.models import (
    AvengerRoom,
    BuildAttachment,
    CatalogueObject,
    ClassDefinition,
    Soldier,
    SoldierStatValue,
)


def ensure_avenger_rooms(playthrough):
    if len(playthrough.avenger_rooms) == 12: return playthrough.avenger_rooms
    for row in range(1, 5):
        for column in range(1, 4):
            if not AvengerRoom.query.filter_by(playthrough_id=playthrough.id, row=row, column=column).first(): db.session.add(AvengerRoom(playthrough=playthrough, row=row, column=column))
    db.session.commit(); return playthrough.avenger_rooms

def visible_catalogue(playthrough, object_type):
    pack_ids = [pack.id for pack in playthrough.content_packs]
    return CatalogueObject.query.filter(CatalogueObject.content_pack_id.in_(pack_ids), CatalogueObject.object_type == object_type, CatalogueObject.enabled.is_(True)).all() if pack_ids else []

def set_room(playthrough, room_id, facility_id=None, planned_facility_id=None, room_state=None, planning_status=None):
    room = AvengerRoom.query.filter_by(id=room_id, playthrough_id=playthrough.id).first_or_404()
    if facility_id is not None and facility_id != "":
        allowed = {obj.id for obj in visible_catalogue(playthrough, "facility")}
        if int(facility_id) not in allowed: raise ValueError("Facility is not available in this playthrough")
        room.facility_id = int(facility_id)
    elif facility_id == "": room.facility_id = None
    if planned_facility_id is not None: room.planned_facility_id = int(planned_facility_id) if planned_facility_id else None
    if room_state is not None: room.room_state = room_state
    if planning_status is not None: room.planning_status = planning_status
    db.session.commit(); return room

def create_soldier(playthrough, class_definition_id=None, rank="Rookie", **fields):
    soldier = Soldier(playthrough=playthrough, class_definition_id=class_definition_id, rank=rank, **fields); db.session.add(soldier); db.session.flush()
    if class_definition_id:
        cls = db.session.get(ClassDefinition, class_definition_id)
        for default in cls.defaults:
            db.session.add(SoldierStatValue(soldier=soldier, stat_definition_id=default.stat_definition_id, suggested_value=default.value, recorded_value=default.value, is_recorded=False))
    db.session.commit(); return soldier

def attachment_compatible(build, attachment_id):
    attachment = db.session.get(CatalogueObject, attachment_id)
    if not attachment: return False
    return bool(attachment.metadata_json and attachment.metadata_json.get("compatible_any")) or any((row.compatible_item_id == build.base_item_id or row.compatible_item_type == build.base_item.object_type) for row in attachment.compatibility_rules)

def add_attachment(build, attachment_id, slot_type="custom"):
    if not build.compatibility_override and not attachment_compatible(build, attachment_id): raise ValueError("Attachment is not compatible with this build")
    link = BuildAttachment(build=build, attachment_id=attachment_id, slot_type=slot_type); db.session.add(link); db.session.commit(); return link
