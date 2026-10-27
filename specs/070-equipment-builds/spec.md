# Equipment build specification

Named weapon and armour builds belong to a user and playthrough. They reference generic catalogue items and attachment components. Compatibility is represented by data rows matching item type, item identity, and/or extensible slot type; Python must not contain item-specific compatibility branches. An explicit per-build override permits incomplete custom metadata.

Acceptance criteria: weapon/armour builds support multiple compatible components, reject incompatible components unless override is enabled, can be cloned and assigned to a soldier, and remain isolated by playthrough. Custom catalogue items are selectable.
