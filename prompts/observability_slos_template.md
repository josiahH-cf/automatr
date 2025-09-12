# quality.observability_slos Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Define metrics & units, tracing/logging requirements, SLO targets & error budget policy, and dashboard/alerts with runbooks.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: quality.observability_slos
schema_ref: urn:automatr:schema:capsule:<feature_id>:quality.observability_slos:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Metrics and Units`
- `## Tracing and Logging`
- `## SLO Targets and Error Budget`
- `## Dashboard and Alerts`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: quality.manual_tests`.
