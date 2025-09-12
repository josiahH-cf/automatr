# planning.concurrency_model Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Define concurrency model, isolation rules, ordering/delivery semantics, cancellation/timeout, retry budgets, and redelivery behavior.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: planning.concurrency_model
schema_ref: urn:automatr:schema:capsule:<feature_id>:planning.concurrency_model:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sections
- `## Model Overview`
- `## Isolation Rules`
- `## Ordering and Delivery Semantics`
- `## Cancellation and Timeout`
- `## Retry Budgets and Redelivery`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: planning.sync_policies`.
