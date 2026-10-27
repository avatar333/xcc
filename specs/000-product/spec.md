# Product specification

XCOM Campaign Planner is a self-hosted Flask application for recording and planning multiple XCOM campaigns. It will support users, playthroughs, content packs, a namespaced object catalogue, local image assets, Avenger facilities, soldiers and units, statistics, weapon/armour builds, attachments and upgrades, research, prerequisite graphs, research queues, acquired/unlocked/researched state, and community-mod/custom objects.

The first releases establish ownership, content-pack composition, and catalogue foundations before gameplay workflows. Users own playthroughs and custom content; a playthrough can activate multiple compatible packs.

## Acceptance criteria

- A local user can authenticate and see a selected campaign context.
- Built-in XCOM 2 Base, WotC, and LWotC packs have conceptual dependencies.
- Catalogue records are namespaced by pack and can carry local, attributed assets.
- The application remains usable without copyrighted bundled game assets.
