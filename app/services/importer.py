from pathlib import Path

import yaml

from app import db
from app.models import CatalogueObject, ContentPack, ResearchPrerequisite, ResearchUnlock


def import_pack(path):
    data = yaml.safe_load(Path(path).read_text())
    pack = ContentPack.query.filter_by(slug=data["slug"]).first()
    if not pack:
        pack = ContentPack(slug=data["slug"], name=data["name"], version=str(data.get("version", "1.0")), description=data.get("description", ""), built_in=True)
        db.session.add(pack); db.session.flush()
    for item in data.get("objects", []):
        obj = CatalogueObject.query.filter_by(content_pack_id=pack.id, object_type=item["object_type"], external_key=item["external_key"]).first()
        if not obj: obj = CatalogueObject(content_pack=pack, external_key=item["external_key"], object_type=item["object_type"])
        obj.name = item["name"]; obj.description = item.get("description", "")
        db.session.add(obj)
    for edge in data.get("prerequisites", []):
        node = CatalogueObject.query.filter_by(content_pack_id=pack.id, external_key=edge["node"]).first(); prerequisite = CatalogueObject.query.filter_by(content_pack_id=pack.id, external_key=edge["prerequisite"]).first()
        if node and prerequisite and not ResearchPrerequisite.query.filter_by(node_id=node.id, prerequisite_id=prerequisite.id).first(): db.session.add(ResearchPrerequisite(node=node, prerequisite=prerequisite))
    for edge in data.get("unlocks", []):
        research = CatalogueObject.query.filter_by(content_pack_id=pack.id, external_key=edge["research"]).first(); unlocked = CatalogueObject.query.filter_by(content_pack_id=pack.id, external_key=edge["unlocked"]).first()
        if research and unlocked and not ResearchUnlock.query.filter_by(research_id=research.id, unlocked_id=unlocked.id).first(): db.session.add(ResearchUnlock(research=research, unlocked=unlocked))
    db.session.commit()
    return pack
