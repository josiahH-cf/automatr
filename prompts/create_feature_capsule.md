# Create Feature Capsule (Launcher)

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Mission
- Create a new feature capsule under `/features/<feature_id>/` and populate documents using templates in `/prompts/`. Do not generate application code.

Initialization
- Generate a unique `feature_id` (kebab-case, 3–50 chars; use `-vN` only for parallel incompatible generations).
- Create `/features/<feature_id>/` and `/features/<feature_id>/reports/`.
- Each Markdown document must start with headers (no owner):
```
feature_id: <feature_id>
doc_type: <doc_type>
schema_ref: urn:automatr:schema:capsule:<feature_id>:<doc_type>:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Unified UNKNOWN Summary
- Every document includes a table:
`ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`
- Write unresolved items into `assumptions.md` and echo them in each doc’s UNKNOWN Summary.

Sequence
- Generate documents in this order, validating after each step:
`vision.md → exploration.md → intent_card.md → output_contract.schema.json → action_budget.md → concurrency_model.md → sync_policies.md → reference_set.md → assumptions.md → evaluation_and_tripwires.md → meta_prompts.md → test_plan.md → runtime_concurrency_tests.md → observability_slos.md → reports/manual_tests.md → reports/chaos_results.md → audit_log.md → changelog_entry → validation_report.md → phase_transition.md`.

- Validation Gates
- Run the validator immediately after each document with per-step logging:
  `FEATURE_ID=<feature_id> DOC_PATH=<path/to/doc> STEP=<n> bash capsule/reports/validation/validate_all.sh`
- It scans `/capsule/**` and `/features/**` for:
  - Header presence/order; canonical `schema_ref` URN
  - `prompts/registry.json` round‑trip
  - Acceptance ↔ `output_contract.schema.json.required` 1:1 mapping (if `required` is non‑empty)
  - Concurrency tuple presence and unit consistency (intent_card, action_budget, output_contract)
  - No prompt leakage / forbidden patterns; size policy (~800 soft alert, 1600 hard confirm)
- Gate behavior:
  - PASS → proceed
  - WARN → proceed and append to `/features/<feature_id>/reports/creation_run.md`
  - FAIL → stop and surface STOP/NEED messages
- At 1600 tokens (hard threshold), require explicit approval before continuing. If approved, re-run validator with `VALIDATION_ALLOW_HARD_SIZE=1`.

Outputs
- `/features/<feature_id>/reports/creation_run.md` with Q/A, validations, and decisions
- `/features/<feature_id>/reports/implementation_brief.md` when all docs pass with no High‑impact unknowns
- On critical blockers: `/features/<feature_id>/reports/creation_blockers.md`
