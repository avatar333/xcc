# Architecture specification

Use a Flask application factory, SQLAlchemy models, Flask-Migrate/Alembic, Flask-Login, Jinja, Bootstrap, HTMX/Alpine where useful, and pytest/ruff. Routes are orchestration only; domain behavior belongs in services. SQLite is the default deployment database.

Content packs are first-class records with slug, version, description, enabled/built-in flags, owner, and parent dependency. Catalogue objects use `(pack, object_type, external_key)` identity. A generic catalogue entity accommodates future types with relational tables for important relationships and optional JSON metadata only for genuinely flexible attributes.

Assets are metadata rows pointing to files outside SQLite. Uploads are validated and stored locally; source, reference, attribution, and fallback behavior are explicit. No production scraping or blind redistribution is permitted.

## Acceptance criteria

- `create_app()` can run against an isolated SQLite database.
- migrations can be initialized and upgraded with Flask-Migrate.
- authentication, ownership filters, and pack relationships are represented relationally.
