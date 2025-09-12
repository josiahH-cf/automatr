# Scaffolding Prompt Library

This repository is in scaffolding mode. Prompts in this folder generate documentation and contracts only — not application features or code.

Folder roles
- `/prompts/` — Template library and orchestration (launcher/controller prompts).
- `/capsule/` — Legacy scaffolding artifacts and program reports. Validation scripts live under `/capsule/reports/validation/`.
- `/features/` — Empty root for future generated feature capsules (`/features/<feature_id>/`).

Start here
- `prompts/create_feature_capsule.md` — launcher prompt for creating a new feature capsule.
- `prompts/run_capsule_chain.md` — controller that orchestrates sequential document generation with validation gates.

Doc headers (for generated Markdown; no owner field)
```
feature_id: <feature_id>
doc_type: <doc_type>
schema_ref: urn:automatr:schema:capsule:<feature_id>:<doc_type>:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

UNKNOWN Summary (shared table schema)
`ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

Validators
- Run `bash capsule/reports/validation/validate_all.sh` after each document. It scans `/capsule/**` and `/features/**` and enforces:
  - Header presence/order; canonical URN for `schema_ref`
  - `prompts/registry.json` round‑trip
  - Acceptance ↔ `output_contract.schema.json.required` mapping (if keys present)
  - Concurrency tuple presence + unit consistency (when applicable)
  - No prompt leakage; size policy (~800 soft alert, 1600 hard confirm)

