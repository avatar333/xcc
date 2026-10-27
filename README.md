# XCOM Campaign Planner

Self-hosted Flask application for planning XCOM 2 campaigns across XCOM 2, War of the Chosen, Long War of the Chosen, and custom content packs.

## Architecture

The application uses a Flask factory, SQLAlchemy/SQLite, Flask-Migrate, Flask-Login, Jinja templates, Bootstrap, and Cytoscape.js for dependency graphs. Content packs namespace immutable catalogue data. Playthroughs own campaign state such as Avenger rooms, soldiers, research state, queues, and equipment builds. Assets are stored as local files with source metadata rather than SQLite blobs.

## Local setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/flask --app 'app:create_app()' run --debug
```

The development bootstrap seeds `admin` / `admin123`; change this password before exposing the application. The default database is `instance/xcom.sqlite3`.

## Database and content

Use Flask-Migrate for deployed databases:

```bash
.venv/bin/flask --app 'app:create_app()' db upgrade
```

Curated YAML packs live in `data/packs/`. Import them from an application shell or management command using `app.services.importer.import_pack(path)`; imports are idempotent. Custom catalogue objects can be added from Catalogue and uploaded images are kept in local media storage with generated filenames.

## Tests and backup

```bash
.venv/bin/pytest -q
.venv/bin/ruff check .
```

Back up the SQLite database and the configured upload directory together. Do not scrape or redistribute copyrighted game assets without permission; use permitted local assets and retain attribution metadata.

## Screenshots

Screenshots will be added here as the UI stabilizes.
