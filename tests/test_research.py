import pytest

from app import db
from app.models import (
    CatalogueObject,
    ContentPack,
    Playthrough,
    ResearchPrerequisite,
    ResearchUnlock,
    User,
)
from app.services.importer import import_pack
from app.services.research import (
    ResearchCycleError,
    add_to_queue,
    prerequisites_for,
    remove_from_queue,
    set_state,
    unlocks_for,
)


def setup_graph(app):
    with app.app_context():
        pack = ContentPack.query.filter_by(slug="wotc").one(); other = ContentPack(slug="research-custom", name="Research Custom", owner=User.query.filter_by(username="admin").one()); db.session.add(other); db.session.flush(); playthrough = Playthrough(owner=other.owner, name="Research", content_packs=[pack, other]); db.session.add(playthrough); db.session.flush()
        a = CatalogueObject(content_pack=other, object_type="research", external_key="a", name="A"); b = CatalogueObject(content_pack=other, object_type="research", external_key="b", name="B"); c = CatalogueObject(content_pack=other, object_type="weapon", external_key="c", name="C"); db.session.add_all([a, b, c]); db.session.flush(); db.session.add_all([ResearchPrerequisite(node=b, prerequisite=a), ResearchPrerequisite(node=c, prerequisite=b), ResearchUnlock(research=b, unlocked=c)]); db.session.commit(); return playthrough.id, a.id, b.id, c.id

def test_transitive_forward_and_queue_states(app):
    playthrough_id, a_id, b_id, c_id = setup_graph(app)
    with app.app_context():
        playthrough = db.session.get(Playthrough, playthrough_id); result = prerequisites_for(playthrough, c_id); assert {node.id for node in result["nodes"]} == {a_id, b_id, c_id}; assert unlocks_for(playthrough, b_id)["edges"] == [(b_id, c_id)]; set_state(playthrough, b_id, "Completed"); item = add_to_queue(playthrough, b_id); assert item.position == 1; remove_from_queue(playthrough, b_id)

def test_cycle_detection_and_pack_isolation(app):
    playthrough_id, a_id, b_id, _ = setup_graph(app)
    with app.app_context():
        playthrough = db.session.get(Playthrough, playthrough_id); db.session.add(ResearchPrerequisite(node_id=a_id, prerequisite_id=b_id)); db.session.commit()
        with pytest.raises(ResearchCycleError): prerequisites_for(playthrough, b_id)
        base_only = Playthrough(owner=playthrough.owner, name="Base only", content_packs=[ContentPack.query.filter_by(slug="xcom2-base").one()]); db.session.add(base_only); db.session.commit(); assert base_only.id != playthrough.id

def test_research_import_is_idempotent(app):
    with app.app_context():
        pack = import_pack("data/packs/wotc-research-subset.yaml"); first = CatalogueObject.query.filter_by(content_pack_id=pack.id, external_key="magnetic-weapons").count(); import_pack("data/packs/wotc-research-subset.yaml"); assert CatalogueObject.query.filter_by(content_pack_id=pack.id, external_key="magnetic-weapons").count() == first == 1
