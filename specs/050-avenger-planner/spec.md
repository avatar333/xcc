# Avenger 3×4 planner specification

Each playthrough owns exactly twelve rooms arranged in three columns and four rows. Room condition is independent of the facility placed in the room. Conditions are `Alien Debris`, `Alien Machinery`, `Exposed Power Coil`, and `Cleared / EMPTY`. Actual facility and planned facility are separate references so the grid can record reality and future intent without mutating catalogue data.

Facilities are catalogue objects scoped to content packs. A playthrough sees facilities from its active packs only. Canonical imported records retain source references; vanilla, WotC, and LWotC records are not merged.

Acceptance criteria: twelve deterministic rooms exist per playthrough; coordinates are unique and valid; placement, replacement, clearing, room-state changes, and planned/building/built states persist; two playthroughs cannot see or mutate one another's rooms; only facilities from active packs appear.
