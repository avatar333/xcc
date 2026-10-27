from app import db
from app.models import BuildAttachment, EquipmentBuild


def clone_build(build, owner, playthrough):
    clone = EquipmentBuild(owner=owner, playthrough=playthrough, name=f"{build.name} Copy", build_type=build.build_type, base_item_id=build.base_item_id, purpose=build.purpose, notes=build.notes, tags=build.tags, compatibility_override=build.compatibility_override); db.session.add(clone); db.session.flush()
    for item in build.attachments: db.session.add(BuildAttachment(build=clone, attachment_id=item.attachment_id, slot_type=item.slot_type))
    db.session.commit(); return clone
