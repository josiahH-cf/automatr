# planning.reference_set Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Provide 3 positive and 3 negative examples; a glossary with ≥5 terms; and note ordering/dedup/race‑prone patterns.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: planning.reference_set
schema_ref: urn:automatr:schema:capsule:<feature_id>:planning.reference_set:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Positive Examples`
- `## Counter-Examples`
- `## Glossary`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: governance.evaluation_and_tripwires`.
