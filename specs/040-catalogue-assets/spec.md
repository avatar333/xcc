# Generic catalogue and assets

Catalogue identity is namespaced by content pack and external key, with extensible object types including facility, research, autopsy, shadow_project, proving_ground_project, weapon, armour, weapon_attachment, armour_attachment, utility_item, class, ability, resource, technology, and other. Custom objects belong to a user-owned custom pack. Assets point to local files and retain role/source/attribution/alt text/primary metadata.

Pack imports use version-controlled YAML/JSON under `data/packs/`; imports are idempotent and never scrape from the application. Future playthrough visibility must be resolved through activated packs and ownership.

## Acceptance criteria and tests

- Same external key is allowed across packs but not within one pack/type.
- Manual custom weapons, armour, and attachments can be created with optional validated images.
- Repeating an import updates or reuses records without duplicates.
- Invalid image extensions are rejected and SQLite contains no binary image data.
