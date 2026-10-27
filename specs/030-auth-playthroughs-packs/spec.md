# Users, playthroughs, and content packs

Users authenticate through Flask-Login. Passwords are hashed. Each playthrough has one owner, timestamps, notes, archive state, and a many-to-many relationship with compatible content packs. Built-in packs are seeded idempotently; WotC depends on Base and LWotC depends on WotC.

## Acceptance criteria and tests

- `admin/admin123` works only through secure hash verification.
- Anonymous users are redirected from protected pages; logout invalidates the session.
- A user cannot view or mutate another user's playthrough.
- Create, archive, and pack attachment work for an owner.
- Dependency metadata is preserved and pack identifiers are unique.
