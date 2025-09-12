# quality.report.manual_tests Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Produce a manual test run report capturing executed tests, results, and links to logs. Output is written to `/features/<feature_id>/reports/manual_tests.md` (or legacy `/capsule/<feature_id>/reports/manual_tests.md`).

Inputs Required
- feature_id (kebab-case)
- Reference to `quality.manual_tests` plan if available
- Links or paths to log artifacts

Follow-up Rule
- Ask unlimited follow-up questions; record unresolved items in an `UNKNOWN Summary` section.

Generation Instructions
- Header fields (exact order):
  - `feature_id: <feature_id>`
  - `doc_type: quality.report.manual_tests`
  - `schema_ref: urn:automatr:schema:capsule:<feature_id>:quality.report.manual_tests:v1@<version>`
  - `version: <semver>`
  - `updated: <YYYY-MM-DD>`
- Sections:
  - `## Test Runs`
  - `## Results Summary`
  - If any failure occurred, add an item in UNKNOWN Summary with `Impact = High` and link to evidence.
  - `## UNKNOWN Summary`

Output Requirement
- Output only the document body and append `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields valid (feature_id regex, SemVer, correct doc_type and schema_ref URN).
- Both sections present and non-empty (or explicitly state None).
- UNKNOWN Summary included when open items remain.
