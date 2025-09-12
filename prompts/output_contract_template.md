# planning.output_contract Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Guide generation of `output_contract.schema.json` defining `$id`, `version`, `required` keys, folder rules, validation path, idempotency/dedup fields, transaction boundaries, and permitted mutation patterns.

Header (embedded in schema fields)
- `$id`: `urn:automatr:schema:capsule:<feature_id>:planning.output_contract:v1`
- `version`: `0.1.0`

Sections/Fields (fill with actual values; placeholders allowed during scaffolding)
```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:automatr:schema:capsule:<feature_id>:planning.output_contract:v1",
  "title": "<TBD>",
  "description": "<TBD>",
  "version": "0.1.0",
  "type": "object",
  "required": [],
  "properties": {},
  "concurrency_targets": {
    "throughput_rps": 0,
    "latency_ms": { "p50": 0, "p95": 0, "p99": 0 },
    "error_budget_pct": 0,
    "window_days": 30
  },
  "folder_rules": { "paths": [] },
  "validation_path": "/features/<feature_id>/reports/validation.json",
  "idempotency": { "keys": [], "dedup_strategy": "<TBD>" },
  "transaction_boundaries": { "unit": "<TBD>", "consistency_model": "<TBD>" },
  "permitted_mutations": [ "<append-only|update|delete-limited>" ]
}
```

UNKNOWN Summary (record unresolved items in assumptions):
`ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

Unit Conventions
- `throughput_rps` in requests per second (rps)
- `latency_ms` in milliseconds
- `error_budget_pct` as percentage (0–100)
- `window_days` as integer days (e.g., 30)

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: planning.action_budget`.

Versioning and Propagation
- Treat this schema as the single source of truth during the capsule run.
- On changes:
  - Bump SemVer: PATCH for clarifications, MINOR for new optional keys, MAJOR for changes to required/constraints.
  - Keep `$id` suffix `v<major>` aligned with SemVer MAJOR when MAJOR bumps occur.
  - Update dependent docs (intent_card mapping, action_budget, manual_tests) and re-run validation.
  - Use helper: `python3 capsule/reports/validation/bump_schema_and_sync.py --feature-id <feature_id> --bump {patch|minor|major} --note "<why>" --run-validate`.
