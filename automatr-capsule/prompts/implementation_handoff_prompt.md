% Implementation Handoff Prompt (Bundle‑Driven, Code Focus)

You are my implementation model. Treat the attached bundle under `final_feature_documents/{{FEATURE_ID}}-*` as the authoritative requirements. Implement the feature in this codebase so that the acceptance criteria, schema, and tests implied by the docs are satisfied on the first run.

Scope
- Read‑only planning docs. Write code, tests, and configuration changes necessary to satisfy requirements.
- Do not edit the planning docs; if constraints force deviations, list them with rationale.

Authoritative inputs (expected files in bundle)
- `intent_card.md`: goal, scope, risks; “## Checklist ↔ Schema Mapping”; “## Concurrency Targets”.
- `output_contract.schema.json`: canonical required keys + properties; `concurrency_targets` object.
- `vision.md`, `exploration.md` (with “## UNKNOWN Summary”), `assumptions.md`, `reference_set.md`.
- `observability_slos.md`, `concurrency_model.md`, `action_budget.md` (with “## Concurrency Budget”).
- `sync_policies.md`, `test_plan.md`, `manual_tests.md`, `runtime_concurrency_tests.md`.
- `validation_report.md`, `phase_transition.md`, `audit_log.md`.

Non‑negotiables
- Acceptance↔Schema alignment: implement code that produces outputs matching `output_contract.schema.json` for all keys in `required[]`.
- Concurrency: respect tuple and budget (throughput_rps, p95 latency_ms, error_budget_pct, window_days) in runtime paths and tests.
- Testing: implement tests per `test_plan.md` and `manual_tests.md` so they pass.

Output
- A minimal, correct implementation that satisfies acceptance criteria and tests.
- Notes on any deviations from docs (if any) and rationale.

