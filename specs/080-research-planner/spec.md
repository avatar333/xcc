# Research dependency graph and planner

Research-like catalogue objects use existing namespaced catalogue identity and may be typed `research`, `autopsy`, `shadow_project`, `proving_ground_project`, `technology`, or another supported type. `ResearchPrerequisite` and `ResearchUnlock` are explicit many-to-many edges; prerequisites and unlocks may target any catalogue object in the same compatible pack set.

Playthrough state is stored separately from canonical catalogue data and supports Unknown, Available, Planned, In Progress, Completed, Unlocked, and Acquired. A queue stores ordered research nodes per playthrough. The graph service traverses backward for “How do I unlock this?” and forward for “What will this unlock?”, tracks visited nodes, detects cycles, and reports them without recursion failure.

Acceptance criteria: zero/one/multiple/transitive prerequisites work; forward unlocks work; queue ordering and completion persist; state badges and prerequisite warnings are shown; pack isolation is enforced; custom nodes work; invalid cycles produce a useful error; graph UI supports Cytoscape zoom, pan, fit, emphasis, images where available, and node details.
