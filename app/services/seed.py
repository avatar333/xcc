from app import db
from app.models import (
    AttachmentCompatibility,
    CatalogueObject,
    ClassDefinition,
    ContentPack,
    ResearchPrerequisite,
    ResearchUnlock,
    StatDefinition,
    User,
)


def validate_pack_dependencies(packs):
    selected = {pack.id for pack in packs}
    return all(pack.parent_id is None or pack.parent_id in selected for pack in packs)


def seed_builtin_packs():
    packs = [("xcom2-base", "XCOM 2 Base", None), ("wotc", "War of the Chosen", "xcom2-base"), ("lwotc", "Long War of the Chosen", "wotc")]
    for slug, name, parent_slug in packs:
        pack = ContentPack.query.filter_by(slug=slug).first() or ContentPack(slug=slug, name=name, built_in=True)
        if parent_slug: pack.parent = ContentPack.query.filter_by(slug=parent_slug).first()
        db.session.add(pack)
    db.session.commit()
    seed_reference_data()

def seed_reference_data():
    wotc = ContentPack.query.filter_by(slug="wotc").one(); base = ContentPack.query.filter_by(slug="xcom2-base").one(); lwotc = ContentPack.query.filter_by(slug="lwotc").one()
    facilities = ["Guerrilla Tactics School", "Laboratory", "Workshop", "Power Relay", "Resistance Comms", "Proving Ground", "Defense Matrix", "Psi Lab", "Shadow Chamber", "Infirmary", "Training Center", "Resistance Ring"]
    for name in facilities: ensure_object(wotc, "facility", name)
    for name in ["Guerrilla Tactics School", "Laboratory", "Workshop", "Power Relay", "Resistance Comms", "Proving Ground", "Advanced Warfare Center", "Psi Lab", "Shadow Chamber", "Defense Matrix"]: ensure_object(base, "facility", name)
    for name in ["Assault", "Gunner", "Grenadier", "Ranger", "Sharpshooter", "Shinobi", "Specialist", "Technical", "Psi Operative", "Reaper", "Skirmisher", "Templar", "SPARK"]: ensure_class(wotc, name, "XCOM 2 WotC Manual / UFOpaedia")
    for name in ["Assault", "Gunner", "Grenadier", "Ranger", "Sharpshooter", "Shinobi", "Specialist", "Technical", "Psi Operative", "Reaper", "Skirmisher", "Templar", "SPARK"]: ensure_class(lwotc, name, "Long War of the Chosen Soldier Overview")
    for name, key in [("Health", "health"), ("Aim", "aim"), ("Mobility", "mobility"), ("Will", "will"), ("Dodge", "dodge"), ("Defense", "defense"), ("Hacking", "hacking"), ("Psi Offense", "psi_offense"), ("Armor", "armor"), ("Combat Intelligence", "combat_intelligence")]:
        stat = StatDefinition.query.filter_by(content_pack_id=wotc.id, key=key).first() or StatDefinition(content_pack=wotc, key=key, name=name); db.session.add(stat)
    for name in ["Assault Rifle", "Shotgun", "Sniper Rifle", "Cannon", "Magnetic Rifle", "Plasma Rifle", "Kevlar Armour", "Predator Armour"]: ensure_object(wotc, "weapon" if "Armour" not in name else "armour", name)
    for name in ["Scope", "Laser Sight", "Repeater", "Hair Trigger", "Expanded Magazine", "Autoloader", "Stock"]:
        attachment = ensure_object(wotc, "weapon_attachment", name)
        if not AttachmentCompatibility.query.filter_by(attachment_id=attachment.id, compatible_item_type="weapon").first(): db.session.add(AttachmentCompatibility(attachment=attachment, compatible_item_type="weapon", slot_type="weapon_attachment"))
    seed_research(wotc)
    db.session.commit()

def seed_research(pack):
    definitions = {"Modular Weapons": "research", "Magnetic Weapons": "research", "Hybrid Materials": "research", "Plated Armor": "research", "Alien Biotech": "research", "Resistance Communications": "research", "ADVENT Officer Autopsy": "autopsy", "Proving Ground": "facility", "Magnetic Rifle": "weapon", "Predator Armour": "armour", "Resistance Comms": "facility"}
    nodes = {name: ensure_object(pack, kind, name) for name, kind in definitions.items()}
    for node, prerequisite in [("Magnetic Weapons", "Modular Weapons"), ("Plated Armor", "Hybrid Materials"), ("Resistance Communications", "Alien Biotech")]:
        if not ResearchPrerequisite.query.filter_by(node_id=nodes[node].id, prerequisite_id=nodes[prerequisite].id).first(): db.session.add(ResearchPrerequisite(node=nodes[node], prerequisite=nodes[prerequisite]))
    for research, unlocked in [("Magnetic Weapons", "Magnetic Rifle"), ("Plated Armor", "Predator Armour"), ("ADVENT Officer Autopsy", "Proving Ground"), ("Resistance Communications", "Resistance Comms")]:
        if not ResearchUnlock.query.filter_by(research_id=nodes[research].id, unlocked_id=nodes[unlocked].id).first(): db.session.add(ResearchUnlock(research=nodes[research], unlocked=nodes[unlocked]))

def ensure_object(pack, object_type, name):
    key = name.lower().replace(" ", "-")
    obj = CatalogueObject.query.filter_by(content_pack_id=pack.id, object_type=object_type, external_key=key).first()
    if not obj: obj = CatalogueObject(content_pack=pack, object_type=object_type, external_key=key, name=name, source="XCOM 2 / War of the Chosen reference data"); db.session.add(obj); db.session.flush()
    return obj

def ensure_class(pack, name, source):
    slug = name.lower().replace(" ", "-")
    if not ClassDefinition.query.filter_by(content_pack_id=pack.id, slug=slug).first(): db.session.add(ClassDefinition(content_pack=pack, slug=slug, name=name, source=source))

def seed_admin():
    if not User.query.filter_by(username="admin").first():
        user = User(username="admin"); user.set_password("admin123"); db.session.add(user); db.session.commit()
