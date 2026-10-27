# Codex handoff

## Completed work

- Added Flask factory, SQLite/SQLAlchemy, Flask-Migrate integration, Flask-Login, Jinja templates, Bootstrap styling, and pytest/ruff configuration.
- Added SDD product, architecture, UI, auth/playthroughs/packs, and catalogue/assets specifications.
- Added ADRs for content-pack boundaries and file-backed generic catalogue assets.
- Implemented hashed seeded admin, ownership-aware playthrough creation/archive, built-in pack dependency metadata, generic namespaced catalogue objects, custom pack creation, validated local image uploads, and an idempotent YAML import service.
- Added original dark command-interface layout with left navigation and placeholders for future gameplay modules.
- Added Avenger 3×4 room planner with independent room conditions, actual/planned facilities, planning states, pack-filtered facility selection, and campaign isolation.
- Added pack-scoped class definitions, reusable stat definitions/default profiles, soldier records, editable stat values, status/rank fields, and WotC/LWotC class reference seeds.
- Added playthrough-scoped weapon/armour builds, data-driven attachment compatibility, custom override support, cloning, and soldier assignment.
- Added SDD specifications for Avenger, soldiers/stats, and equipment builds plus a state/catalogue ADR.
- Added SDD specifications for research planning and integrated dashboard/release checks.
- Added explicit research prerequisite/unlock edges, playthrough object states, ordered research queues, cycle-safe graph traversal, Cytoscape graph rendering/JSON, WotC starter research data, and an idempotent research import shape.
- Replaced the dashboard placeholder with selected-campaign summary cards, quick actions, and persistent feature navigation.
- Added the first Alembic migration revision, empty-database migration smoke coverage, release documentation, intentional image fallback styling, and application-level CSRF protection for browser POST forms.

## Architecture decisions

Content packs are the compatibility and namespace boundary. A generic catalogue entity is shared across future object types. Assets are files plus provenance metadata, never SQLite blobs. Routes remain thin and seed/import behavior is isolated in services.

## Files changed

Added/updated `app/`, `specs/`, `docs/adr/`, `docs/CODEX_HANDOFF.md`, `migrations/README.md`, `data/packs/example.yaml`, `tests/`, and `pyproject.toml`.

## Test commands/results

`.venv/bin/pytest -q` passed: 10 tests. `.venv/bin/ruff check .` passed. `python3 -m compileall -q app tests migrations` and `git diff --check` passed. Empty-database `flask db upgrade` smoke test passed against a temporary SQLite database.

## Known limitations

Local zero-configuration startup still creates the schema for convenience, while deployed databases should use the generated Alembic revision. The research graph uses Cytoscape via CDN and currently has a focused backward explorer; richer forward graph controls and drag/drop queue UI remain future polish. Image cards use the existing fallback rather than bundled game art. Soldier stat defaults are intentionally sparse until difficulty/mod-specific profiles are curated. Full mission gameplay domains remain incomplete. The default password is for local bootstrap only.

## Next logical phase

Add forward/backward graph controls, richer prerequisite warning presentation, and a proper management command for pack imports before broader gameplay modules.
