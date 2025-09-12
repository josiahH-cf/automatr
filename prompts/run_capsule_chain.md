# Run Capsule Chain (Controller)

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Orchestrate sequential generation for a feature capsule using templates in `/prompts/`, enforcing validation gates between steps. No application code is generated.

Inputs
- feature_id (kebab-case, 3–50 chars)
- Feature brief and any prior answers

Process
1) Resolve clarifying questions; prefer inference from repo context.
2) Determine next step:
   - If the current document includes a footer naming the next doc_type(s), honor that.
   - Otherwise, fall back to the fixed sequence below.
3) For each document:
   - Load the matching template from `/prompts/`, generate the document body only (no prompt text), and include the standardized UNKNOWN Summary table.
   - Immediately run the validator with gating and per-step logging:
     `FEATURE_ID=<feature_id> DOC_PATH=<path/to/doc> STEP=<n> [DECISIONS="<notes>"] [LINKS="<path|url>"] bash capsule/reports/validation/validate_all.sh`
   - Gate behavior:
     - PASS → proceed to next document.
     - WARN → proceed and log in `/features/<feature_id>/reports/creation_run.md`.
     - FAIL → stop and surface:
       `STOP: <reason>` and `NEED: <specific fix or answer>`.
   - Size control:
      - Soft alert at ~800 tokens (warn only).
      - Hard confirm at 1600 tokens: pause and require explicit approval. Proceed only if human approval is recorded; then set `VALIDATION_ALLOW_HARD_SIZE=1` when re-running the validator.
   - Schema evolution (single source of truth):
     - If new constraints/fields are discovered, immediately update `/features/<feature_id>/output_contract.schema.json` using:
       `python3 capsule/reports/validation/bump_schema_and_sync.py --feature-id <feature_id> --bump {patch|minor|major} --note "<why>" --run-validate`
     - After the bump, refresh dependent docs where needed:
       - `intent_card.md`: update Acceptance checklist and Checklist ↔ Schema Mapping
       - `action_budget.md`: adjust permitted mutations and boundaries
       - `manual_tests.md`: update tests mapped to required schema keys
       - Concurrency docs if constraints affect throughput/latency/error budget
     - Re-run the validator (as above) to enforce alignment.
4) If validations reveal new constraints, update schema/documents and restart at the earliest dependent step.
5) After completing the full chain, re-execute the validator for a full-tree scan (capsule and features roots):
   `FEATURE_ID=<feature_id> bash capsule/reports/validation/validate_all.sh`
6) Implementable flagging (final gate):
   - Require a clean PASS with no WARN for implementable readiness by running:
     `FEATURE_ID=<feature_id> REQUIRE_IMPLEMENTABLE=1 bash capsule/reports/validation/validate_all.sh`
   - On PASS, the validator appends to `/features/<feature_id>/reports/creation_run.md`:
     `## IMPLEMENTABLE` with status and date, and logs a CHANGES line to `/features/<feature_id>/CHANGELOG.md`.

Sequence
`vision.md → exploration.md → intent_card.md → output_contract.schema.json → action_budget.md → concurrency_model.md → sync_policies.md → reference_set.md → assumptions.md → evaluation_and_tripwires.md → meta_prompts.md → test_plan.md → runtime_concurrency_tests.md → observability_slos.md → reports/manual_tests.md → reports/chaos_results.md → audit_log.md → changelog_entry → validation_report.md → phase_transition.md`.

Validation Gates (enforced by validator scripts)
- Headers and canonical `schema_ref` URN
- Registry round‑trip
- Acceptance ↔ schema.required mapping (if required keys present)
- Concurrency tuple presence + unit consistency (intent_card, action_budget, output_contract)
- No prompt leakage; size soft alert (~800), hard confirm (1600)

Outputs
- Updated docs under `/features/<feature_id>/` and logs under `/features/<feature_id>/reports/`

Notes
- This controller supports both `/features/<feature_id>/` and legacy `/capsule/<feature_id>/` layouts.
