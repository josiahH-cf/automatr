# planning.phase_transition Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Summarize validation, diffs for next phase, idempotence confirmation, and carry‑forward of SLO gaps and open issues.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: planning.phase_transition
schema_ref: urn:automatr:schema:capsule:<feature_id>:planning.phase_transition:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Validation Summary`
- `## Diffs and Next Phase Plan`
- `## Idempotence Confirmation`
- `## SLO Gaps and Open Issues`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: governance.changelog_entry`.
