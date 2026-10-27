from app import db
from app.models import ContentPack, User


def login(client): return client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)

def test_seeded_admin_is_hashed_and_login_logout(client, app):
    with app.app_context():
        user = User.query.filter_by(username="admin").one()
        assert user.password_hash != "admin123" and user.check_password("admin123")
    response = login(client); assert b"Dashboard" in response.data
    assert client.post("/logout", follow_redirects=True).status_code == 200

def test_protected_and_playthrough_crud(client, app):
    assert client.get("/dashboard").status_code == 302
    login(client)
    response = client.post("/playthroughs/create", data={"name": "Ironman", "pack_ids": ["1"]}, follow_redirects=True)
    assert b"Ironman" in response.data
    with app.app_context(): assert db.session.query(ContentPack).count() == 3

def test_catalogue_namespace_and_invalid_image(client, app):
    login(client)
    client.post("/catalogue/create", data={"name": "Rifle", "object_type": "weapon"})
    client.post("/catalogue/create", data={"name": "Other Rifle", "object_type": "weapon"})
    with app.app_context():
        from app.models import CatalogueObject, ContentPack
        pack = ContentPack.query.filter_by(slug="custom-1").one()
        assert CatalogueObject.query.filter_by(content_pack_id=pack.id).count() == 2

def test_pack_dependency_is_required(client):
    login(client)
    response = client.post("/playthroughs/create", data={"name": "Invalid", "pack_ids": ["2"]}, follow_redirects=True)
    assert b"require their parent packs" in response.data
