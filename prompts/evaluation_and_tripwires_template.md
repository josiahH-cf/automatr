# governance.evaluation_and_tripwires Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Define do‑not‑do list, 5–8 tripwires with stop messages, a diff snippet rule, and concurrency tripwires with numeric thresholds.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: governance.evaluation_and_tripwires
schema_ref: urn:automatr:schema:capsule:<feature_id>:governance.evaluation_and_tripwires:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Do-Not-Do List`
- `## Tripwires`
- `## Diff Snippet Rule`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: quality.observability_slos`.
