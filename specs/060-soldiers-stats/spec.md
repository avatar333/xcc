# Soldiers, classes, and stats specification

Soldiers belong to a playthrough and are owned through its user. Classes and reusable stat definitions are content-pack data. Class defaults are relational profile rows, while a soldier's current values are editable overrides with a `is_recorded` distinction from suggested defaults. No fixed stat list is embedded in the soldier table, allowing WotC, LWotC, and mods to add or omit stats.

Acceptance criteria: a soldier can be created with an available pack-scoped class and optional rank; defaults are copied when defined, missing defaults remain editable/empty; actual values can differ from suggestions; class changes preserve identity and update only applicable suggestions; custom stats and pack-specific classes remain isolated.
