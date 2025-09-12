# planning.vision Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Capture end‑state and rationale, success criteria, non‑goals, and high‑level integration/constraints to guide downstream planning and implementation.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: planning.vision
schema_ref: urn:automatr:schema:capsule:<feature_id>:planning.vision:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Summary`
- `## Success Criteria`
- `## Non-Goals`
- `## Architecture/Integration Notes`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: planning.exploration`.
