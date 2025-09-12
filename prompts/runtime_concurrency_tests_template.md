# quality.runtime_concurrency_tests Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Define schedule fuzzing, chaos and soak tests, load matrix, redelivery and retry verification, and artifact links.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: quality.runtime_concurrency_tests
schema_ref: urn:automatr:schema:capsule:<feature_id>:quality.runtime_concurrency_tests:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Load and Schedule Matrix`
- `## Chaos and Soak Plan`
- `## Redelivery and Retry Verification`
- `## Artifact Links`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: governance.meta_prompts`.
