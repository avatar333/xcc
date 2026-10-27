import pytest

from app import create_app, db


@pytest.fixture()
def app(tmp_path):
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.sqlite'}", "UPLOAD_FOLDER": str(tmp_path / "uploads"), "SECRET_KEY": "test"})
    yield app
    with app.app_context(): db.session.remove(); db.drop_all()

@pytest.fixture()
def client(app): return app.test_client()
