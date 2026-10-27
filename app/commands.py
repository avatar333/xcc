import click
from flask_migrate import stamp, upgrade
from sqlalchemy import inspect, text

from app import db
from app.services.seed import seed_admin, seed_builtin_packs


def register_commands(app):
    @app.cli.command("bootstrap")
    def bootstrap_database():
        """Apply migrations and seed the local built-in reference data."""
        tables = set(inspect(db.engine).get_table_names())
        current_revision = None
        if "alembic_version" in tables:
            current_revision = db.session.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).scalar()
        if "user" in tables and current_revision != "fe0fc60c9974":
            click.echo("Existing schema detected; marking it at the current migration head.")
            stamp(directory="migrations", revision="head")
        elif "user" not in tables:
            upgrade(directory="migrations")
        seed_builtin_packs()
        seed_admin()
        click.echo("Database ready.")
