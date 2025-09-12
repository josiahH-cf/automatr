# quality.report.chaos_results Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Guide a future LLM to produce a chaos test results report summarizing scenarios, outcomes, and issues. Output goes to `capsule/<feature_id>/reports/chaos_results.md`.

Inputs Required
- feature_id (kebab-case)
- Chaos tooling and schedule used, if known
- Links to artifacts and evidence

Follow-up Rule
- Ask unlimited follow-up questions; record unresolved items in an `UNKNOWN Summary` section.

Generation Instructions
- Header fields (exact order):
  - `feature_id: <feature_id>`
  - `doc_type: quality.report.chaos_results`
  - `schema_ref: urn:automatr:schema:capsule:<feature_id>:quality.report.chaos_results:v1@<version>`
  - `version: <semver>`
  - `updated: <YYYY-MM-DD>`
- Sections:
  - `## Scenarios`
  - `## Outcomes`
  - `## Issues`
  - `## UNKNOWN Summary`

Output Requirement
- Output only the document body and append `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields valid and correct.
- All sections present and populated or explicitly noted None.
- UNKNOWN Summary included when open items remain.
