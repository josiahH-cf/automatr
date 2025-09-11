# quality.report.manual_tests Template

Purpose
- Guide a future LLM to produce a manual test run report capturing executed tests, results, and links to logs. Output goes to `capsule/<feature_id>/reports/manual_tests.md`.

Inputs Required
- feature_id (kebab-case), owner (team or human)
- Reference to `quality.manual_tests` plan if available
- Links or paths to log artifacts

Follow-up Rule
- Ask up to 3 clarifying questions; record unresolved items in an `UNKNOWN Summary` section.

Generation Instructions
- Header fields (exact order):
  - `feature_id: <feature-id>`
  - `owner: <team-or-person>`
  - `doc_type: quality.report.manual_tests`
  - `schema_ref: urn:automatr:schema:capsule:<feature_id>:quality.report.manual_tests:v1@<version>`
  - `version: <semver>`
  - `updated: <YYYY-MM-DD>`
- Sections:
  - `## Test Runs`
  - `## Results Summary`
  - `## UNKNOWN Summary`

Output Requirement
- Output only the document body and append `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields valid (feature_id regex, SemVer, correct doc_type and schema_ref URN).
- Both sections present and non-empty (or explicitly state None).
- UNKNOWN Summary included when open items remain.

