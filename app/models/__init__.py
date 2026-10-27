from datetime import UTC, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager

playthrough_packs = db.Table("playthrough_packs", db.Column("playthrough_id", db.Integer, db.ForeignKey("playthrough.id"), primary_key=True), db.Column("content_pack_id", db.Integer, db.ForeignKey("content_pack.id"), primary_key=True))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True); username = db.Column(db.String(80), unique=True, nullable=False); password_hash = db.Column(db.String(255), nullable=False)
    playthroughs = db.relationship("Playthrough", back_populates="owner", cascade="all, delete-orphan"); custom_packs = db.relationship("ContentPack", back_populates="owner")
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class ContentPack(db.Model):
    id = db.Column(db.Integer, primary_key=True); slug = db.Column(db.String(120), unique=True, nullable=False); name = db.Column(db.String(160), nullable=False); version = db.Column(db.String(40), default="1.0"); description = db.Column(db.Text, default=""); built_in = db.Column(db.Boolean, default=False, nullable=False); enabled = db.Column(db.Boolean, default=True, nullable=False); owner_id = db.Column(db.Integer, db.ForeignKey("user.id")); parent_id = db.Column(db.Integer, db.ForeignKey("content_pack.id"))
    owner = db.relationship("User", back_populates="custom_packs"); parent = db.relationship("ContentPack", remote_side=[id]); objects = db.relationship("CatalogueObject", back_populates="content_pack", cascade="all, delete-orphan")

class Playthrough(db.Model):
    id = db.Column(db.Integer, primary_key=True); owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False); name = db.Column(db.String(160), nullable=False); description = db.Column(db.Text, default=""); archived = db.Column(db.Boolean, default=False, nullable=False); created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False); updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    owner = db.relationship("User", back_populates="playthroughs"); content_packs = db.relationship("ContentPack", secondary=playthrough_packs, backref="playthroughs")

class CatalogueObject(db.Model):
    __table_args__ = (db.UniqueConstraint("content_pack_id", "object_type", "external_key", name="uq_pack_object_key"),)
    id = db.Column(db.Integer, primary_key=True); content_pack_id = db.Column(db.Integer, db.ForeignKey("content_pack.id"), nullable=False); external_key = db.Column(db.String(160), nullable=False); object_type = db.Column(db.String(60), nullable=False); name = db.Column(db.String(160), nullable=False); short_name = db.Column(db.String(100)); description = db.Column(db.Text, default=""); notes = db.Column(db.Text, default=""); source = db.Column(db.String(255), default=""); canonical = db.Column(db.Boolean, default=True, nullable=False); enabled = db.Column(db.Boolean, default=True, nullable=False); sort_order = db.Column(db.Integer, default=0, nullable=False); metadata_json = db.Column(db.JSON, default=dict)
    content_pack = db.relationship("ContentPack", back_populates="objects"); assets = db.relationship("Asset", back_populates="catalogue_object", cascade="all, delete-orphan"); compatibility_rules = db.relationship("AttachmentCompatibility", foreign_keys="AttachmentCompatibility.attachment_id", cascade="all, delete-orphan")

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True); object_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False); path = db.Column(db.String(255), nullable=False); role = db.Column(db.String(40), default="icon", nullable=False); source = db.Column(db.String(255), default=""); attribution = db.Column(db.String(255), default=""); alt_text = db.Column(db.String(255), default=""); primary = db.Column(db.Boolean, default=False, nullable=False)
    catalogue_object = db.relationship("CatalogueObject", back_populates="assets")

class AvengerRoom(db.Model):
    __table_args__ = (db.UniqueConstraint("playthrough_id", "column", "row", name="uq_playthrough_room"),)
    id = db.Column(db.Integer, primary_key=True); playthrough_id = db.Column(db.Integer, db.ForeignKey("playthrough.id"), nullable=False); column = db.Column(db.Integer, nullable=False); row = db.Column(db.Integer, nullable=False); room_state = db.Column(db.String(30), default="Alien Debris", nullable=False); facility_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id")); planned_facility_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id")); planning_status = db.Column(db.String(20), default="Built", nullable=False)
    playthrough = db.relationship("Playthrough", backref=db.backref("avenger_rooms", cascade="all, delete-orphan")); facility = db.relationship("CatalogueObject", foreign_keys=[facility_id]); planned_facility = db.relationship("CatalogueObject", foreign_keys=[planned_facility_id])

class StatDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True); content_pack_id = db.Column(db.Integer, db.ForeignKey("content_pack.id")); key = db.Column(db.String(80), nullable=False); name = db.Column(db.String(100), nullable=False); description = db.Column(db.Text, default=""); enabled = db.Column(db.Boolean, default=True, nullable=False)
    content_pack = db.relationship("ContentPack", backref="stat_definitions")

class ClassDefinition(db.Model):
    __table_args__ = (db.UniqueConstraint("content_pack_id", "slug", name="uq_pack_class"),)
    id = db.Column(db.Integer, primary_key=True); content_pack_id = db.Column(db.Integer, db.ForeignKey("content_pack.id"), nullable=False); slug = db.Column(db.String(80), nullable=False); name = db.Column(db.String(100), nullable=False); description = db.Column(db.Text, default=""); source = db.Column(db.String(255), default="")
    content_pack = db.relationship("ContentPack", backref="class_definitions"); defaults = db.relationship("ClassStatDefault", cascade="all, delete-orphan", back_populates="class_definition")

class ClassStatDefault(db.Model):
    id = db.Column(db.Integer, primary_key=True); class_definition_id = db.Column(db.Integer, db.ForeignKey("class_definition.id"), nullable=False); stat_definition_id = db.Column(db.Integer, db.ForeignKey("stat_definition.id"), nullable=False); rank = db.Column(db.String(40), default="Squaddie", nullable=False); value = db.Column(db.Integer)
    class_definition = db.relationship("ClassDefinition", back_populates="defaults"); stat_definition = db.relationship("StatDefinition")

class Soldier(db.Model):
    id = db.Column(db.Integer, primary_key=True); playthrough_id = db.Column(db.Integer, db.ForeignKey("playthrough.id"), nullable=False); class_definition_id = db.Column(db.Integer, db.ForeignKey("class_definition.id")); first_name = db.Column(db.String(80), default=""); last_name = db.Column(db.String(80), default=""); nickname = db.Column(db.String(80), default=""); rank = db.Column(db.String(40), default="Rookie"); status = db.Column(db.String(30), default="Available"); notes = db.Column(db.Text, default=""); portrait_asset_id = db.Column(db.Integer, db.ForeignKey("asset.id")); weapon_build_id = db.Column(db.Integer, db.ForeignKey("equipment_build.id")); armour_build_id = db.Column(db.Integer, db.ForeignKey("equipment_build.id"))
    playthrough = db.relationship("Playthrough", backref=db.backref("soldiers", cascade="all, delete-orphan")); class_definition = db.relationship("ClassDefinition"); stats = db.relationship("SoldierStatValue", cascade="all, delete-orphan", back_populates="soldier")

class SoldierStatValue(db.Model):
    __table_args__ = (db.UniqueConstraint("soldier_id", "stat_definition_id", name="uq_soldier_stat"),)
    id = db.Column(db.Integer, primary_key=True); soldier_id = db.Column(db.Integer, db.ForeignKey("soldier.id"), nullable=False); stat_definition_id = db.Column(db.Integer, db.ForeignKey("stat_definition.id"), nullable=False); suggested_value = db.Column(db.Integer); recorded_value = db.Column(db.Integer); is_recorded = db.Column(db.Boolean, default=False, nullable=False)
    soldier = db.relationship("Soldier", back_populates="stats"); stat_definition = db.relationship("StatDefinition")

class AttachmentCompatibility(db.Model):
    id = db.Column(db.Integer, primary_key=True); attachment_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False); compatible_item_type = db.Column(db.String(60)); compatible_item_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id")); slot_type = db.Column(db.String(60), default="custom")
    attachment = db.relationship("CatalogueObject", foreign_keys=[attachment_id], overlaps="compatibility_rules"); compatible_item = db.relationship("CatalogueObject", foreign_keys=[compatible_item_id])

class EquipmentBuild(db.Model):
    id = db.Column(db.Integer, primary_key=True); owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False); playthrough_id = db.Column(db.Integer, db.ForeignKey("playthrough.id"), nullable=False); name = db.Column(db.String(160), nullable=False); build_type = db.Column(db.String(20), nullable=False); base_item_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False); purpose = db.Column(db.String(160), default=""); notes = db.Column(db.Text, default=""); tags = db.Column(db.String(255), default=""); compatibility_override = db.Column(db.Boolean, default=False, nullable=False)
    owner = db.relationship("User"); playthrough = db.relationship("Playthrough", backref=db.backref("equipment_builds", cascade="all, delete-orphan")); base_item = db.relationship("CatalogueObject", foreign_keys=[base_item_id]); attachments = db.relationship("BuildAttachment", cascade="all, delete-orphan", back_populates="build")

class BuildAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True); build_id = db.Column(db.Integer, db.ForeignKey("equipment_build.id"), nullable=False); attachment_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False); slot_type = db.Column(db.String(60), default="custom", nullable=False)
    build = db.relationship("EquipmentBuild", back_populates="attachments"); attachment = db.relationship("CatalogueObject")

class ResearchPrerequisite(db.Model):
    __table_args__ = (db.UniqueConstraint("node_id", "prerequisite_id", name="uq_research_prerequisite"),)
    id = db.Column(db.Integer, primary_key=True); node_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False); prerequisite_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False)
    node = db.relationship("CatalogueObject", foreign_keys=[node_id], backref="prerequisites"); prerequisite = db.relationship("CatalogueObject", foreign_keys=[prerequisite_id], backref="required_for")

class ResearchUnlock(db.Model):
    __table_args__ = (db.UniqueConstraint("research_id", "unlocked_id", name="uq_research_unlock"),)
    id = db.Column(db.Integer, primary_key=True); research_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False); unlocked_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False)
    research = db.relationship("CatalogueObject", foreign_keys=[research_id], backref="unlocks"); unlocked = db.relationship("CatalogueObject", foreign_keys=[unlocked_id], backref="unlocked_by")

class PlaythroughObjectState(db.Model):
    __table_args__ = (db.UniqueConstraint("playthrough_id", "object_id", name="uq_playthrough_object_state"),)
    id = db.Column(db.Integer, primary_key=True); playthrough_id = db.Column(db.Integer, db.ForeignKey("playthrough.id"), nullable=False); object_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False); state = db.Column(db.String(20), default="Unknown", nullable=False); note = db.Column(db.Text, default="")
    playthrough = db.relationship("Playthrough", backref=db.backref("object_states", cascade="all, delete-orphan")); object = db.relationship("CatalogueObject")

class ResearchQueueItem(db.Model):
    __table_args__ = (db.UniqueConstraint("playthrough_id", "object_id", name="uq_research_queue_item"),)
    id = db.Column(db.Integer, primary_key=True); playthrough_id = db.Column(db.Integer, db.ForeignKey("playthrough.id"), nullable=False); object_id = db.Column(db.Integer, db.ForeignKey("catalogue_object.id"), nullable=False); position = db.Column(db.Integer, nullable=False); completed = db.Column(db.Boolean, default=False, nullable=False)
    playthrough = db.relationship("Playthrough", backref=db.backref("research_queue", cascade="all, delete-orphan")); object = db.relationship("CatalogueObject")

@login_manager.user_loader
def load_user(user_id): return db.session.get(User, int(user_id))
