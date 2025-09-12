# planning.action_budget Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Define edit boundaries, whitelist with dry‑run, denylist, pre‑checks, and side‑effect boundaries.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: planning.action_budget
schema_ref: urn:automatr:schema:capsule:<feature_id>:planning.action_budget:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Editable vs Read-only`
- `## Whitelist (dry-run first)`
- `## Denylist`
- `## Pre-checks`
- `## Side-effect Boundaries`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

Sections
- `## Editable vs Read-only`
- `## Whitelist (dry-run first)`
- `## Denylist`
- `## Pre-checks`
- `## Side-effect Boundaries`
- `## Concurrency Budget`
  - Table: `Throughput (rps) | Latency p50 (ms) | Latency p95 (ms) | Latency p99 (ms) | Error Budget (%) | Window (days)`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: planning.concurrency_model`.
