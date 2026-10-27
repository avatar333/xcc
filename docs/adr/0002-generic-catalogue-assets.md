# ADR 0002: Generic catalogue with file-backed assets

One catalogue entity supports shared presentation and identity across object types. Important relationships will use relational tables; optional metadata may use JSON. Images are file-backed with database metadata for provenance and attribution, avoiding SQLite blobs and untraceable copyrighted content.
