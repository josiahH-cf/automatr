# planning.sync_policies Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Define synchronization primitives, backpressure thresholds and actions, resource quotas and fairness, and scheduling rules for fan‑out/fan‑in.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: planning.sync_policies
schema_ref: urn:automatr:schema:capsule:<feature_id>:planning.sync_policies:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Synchronization Primitives`
- `## Backpressure Policy`
- `## Resource Quotas and Fairness`
- `## Scheduling Rules`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: planning.reference_set`.
