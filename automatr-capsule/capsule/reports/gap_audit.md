# GAP Audit Report

Path: capsule/reports/gap_audit.md

**Overview**
- Date: 2025-09-11
- Repo Base Commit: aa99846a590d321ee4507aa9523a5813dd5b4a96
- Mission: Verify the scaffold against Phase 0–4 plans and invariants; identify gaps, drifts, and unresolved items; confirm readiness for Phase 5.

**Checks Performed and Outcomes**
- Identity handshake
  - Header fields present (feature_id, owner, doc_type, schema_ref, version, updated): PASS
  - schema_ref format and match: PASS — canonical URNs applied across all capsule markdown:
    - `urn:automatr:schema:capsule:<feature_id>:<doc_type>:v1@0.1.0`
  - Downstream echo consistency: PASS — placeholders are consistent across all docs.
- Acceptance ↔ schema mapping
  - Structure present: PASS — `intent_card.md` includes “Checklist → Schema Mapping” table.
  - 1:1 coverage with `output_contract.schema.json.required`: WARN — `required` is empty at skeleton stage.
- Concurrency tuple consistency
  - Presence and unit consistency across `intent_card.md`, `output_contract.schema.json`, `action_budget.md`: WARN — sections exist; values are `<TBD>`.
- Follow-up Q rule
  - UNKNOWN Summary stubs present; no prompt leakage: PASS/N/A (population occurs during generation).
- Size caps & prompt leakage
  - Skeletons are minimal and free of meta-prompt text: PASS.
- Validation & CI wiring
  - Scripts present: PASS — `capsule/reports/validation/` contains feature_id, SemVer, registry, and header checks.
  - Registry round-trip: PASS — templates and `prompts/registry.json` consistent.
  - Header checks wiring: PASS — `validate_all.sh` points to repo root and skips placeholder skeletons (`feature_id: <feature-id>`). Execution succeeds and awaits real docs.
- Closeout confirmation
  - Phase 4 closeout present with resolutions/defaults: PASS.

**UNKNOWN Summary**
| Field | Context | Owner | Next Step |
| --- | --- | --- | --- |
| Metrics stack & units | `observability_slos.md` needs canonical metrics taxonomy and unit conventions. | SRE/Platform Owner | Provide taxonomy/units; update doc. Due: 2025-09-25 |
| Chaos tooling & schedule | `runtime_concurrency_tests.md` needs approved tools and cadence. | QA/Resilience Owner | Specify tools + schedule; update doc. Due: 2025-09-25 |

**Recommended Fixes**
- Completed
  - Applied canonical schema_ref URNs to all capsule markdown headers.
  - Fixed `validate_all.sh` ROOT_DIR and added placeholder skip logic.
- Pending (post‑generation)
  - Populate `output_contract.schema.json.required` and ensure 1:1 mapping from `intent_card.md` Acceptance Checklist.
  - Define concurrency tuple (throughput/latency/error-budget) and align units across `intent_card.md`, `action_budget.md`, and `output_contract.schema.json`.

**Next Action**
- Proceed to Phase 5 end‑to‑end feature workflow test: generate a real capsule (non‑placeholder feature_id), produce documents via templates, and run `capsule/reports/validation/validate_all.sh` to validate headers and schema_ref URNs on concrete artifacts.

## UNKNOWN Summary
ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)
U-001 | What are the canonical metrics and units for SLOs? | Inconsistent observability targets; audits harder to compare | Define metrics taxonomy and unit conventions | Update `quality.observability_slos` during first capsule | Moderate
U-002 | Which chaos tools and schedule are approved? | Gaps in resilience coverage and evidence | Select tooling and cadence with QA/SRE | Update `quality.runtime_concurrency_tests` and reports | Moderate

## Validation Loop (Phase-5 Gate)
- Implemented per-document validation with gating and step logging.
- Script: `capsule/reports/validation/validate_all.sh`
  - Outputs final `GATE: PASS|WARN|FAIL` and STOP/NEED messages on FAIL.
  - Appends to `/features/<feature_id>/reports/creation_run.md` when `FEATURE_ID` and `DOC_PATH` are provided.
  - Produces `/features/<feature_id>/reports/validation_summary.md` per run.
- Hard size threshold requires explicit approval; proceed by setting `VALIDATION_ALLOW_HARD_SIZE=1` and re-running validator.
