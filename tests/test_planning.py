import pytest

from app import db
from app.models import (
    AvengerRoom,
    CatalogueObject,
    ClassDefinition,
    ClassStatDefault,
    ContentPack,
    EquipmentBuild,
    StatDefinition,
)
from app.services.equipment import clone_build
from app.services.gameplay import add_attachment, create_soldier, ensure_avenger_rooms, set_room


def login(client): return client.post("/login", data={"username": "admin", "password": "admin123"})

def make_playthrough(app):
    with app.app_context():
        from app.models import Playthrough, User
        packs = ContentPack.query.filter(ContentPack.slug.in_(["xcom2-base", "wotc", "lwotc"])).all()
        p = Playthrough(owner=User.query.filter_by(username="admin").one(), name="Test campaign", content_packs=packs); db.session.add(p); db.session.commit(); return p.id

def test_avenger_rooms_and_isolation(client, app):
    login(client); first = make_playthrough(app)
    with app.app_context():
        from app.models import Playthrough
        p = db.session.get(Playthrough, first); rooms = ensure_avenger_rooms(p)
        assert len(rooms) == 12 and {(r.row, r.column) for r in rooms} == {(row, col) for row in range(1, 5) for col in range(1, 4)}
        facility = CatalogueObject.query.filter_by(object_type="facility").first(); set_room(p, rooms[0].id, facility_id=facility.id, room_state="Cleared / EMPTY", planning_status="Planned")
        assert rooms[0].facility_id == facility.id and rooms[0].planning_status == "Planned"
        other = Playthrough(owner=p.owner, name="Other", content_packs=p.content_packs); db.session.add(other); db.session.commit(); ensure_avenger_rooms(other)
        assert AvengerRoom.query.filter_by(playthrough_id=other.id, facility_id=facility.id).count() == 0

def test_soldier_defaults_and_custom_stat(app):
    with app.app_context():
        from app.models import Playthrough, User
        p = Playthrough(owner=User.query.filter_by(username="admin").one(), name="Soldier test"); db.session.add(p); db.session.flush()
        pack = ContentPack.query.filter_by(slug="wotc").one(); cls = ClassDefinition.query.filter_by(content_pack_id=pack.id, slug="ranger").one(); stat = StatDefinition(content_pack=pack, key="custom_stat", name="Custom Stat"); db.session.add(stat); db.session.flush(); db.session.add(ClassStatDefault(class_definition=cls, stat_definition=stat, value=7)); db.session.commit()
        soldier = create_soldier(p, cls.id); assert soldier.stats[0].suggested_value == 7 and soldier.stats[0].is_recorded is False

def test_equipment_compatibility_clone_and_override(app):
    with app.app_context():
        from app.models import Playthrough, User
        p = Playthrough(owner=User.query.filter_by(username="admin").one(), name="Build test", content_packs=[ContentPack.query.filter_by(slug="wotc").one()]); db.session.add(p); db.session.flush(); weapon = CatalogueObject.query.filter_by(object_type="weapon").first(); armour = CatalogueObject.query.filter_by(object_type="armour").first(); attachment = CatalogueObject.query.filter_by(object_type="weapon_attachment").first(); build = EquipmentBuild(owner=p.owner, playthrough=p, name="Weapon", build_type="Weapon", base_item=weapon); db.session.add(build); db.session.commit(); add_attachment(build, attachment.id); clone = clone_build(build, p.owner, p); assert len(clone.attachments) == 1
        armour_build = EquipmentBuild(owner=p.owner, playthrough=p, name="Armour", build_type="Armour", base_item=armour); db.session.add(armour_build); db.session.commit()
        with pytest.raises(ValueError): add_attachment(armour_build, attachment.id)
        armour_build.compatibility_override = True; db.session.commit(); add_attachment(armour_build, attachment.id); assert len(armour_build.attachments) == 1
