# quality.validation_report Template

Purpose
- Guide a future LLM to produce a validation report summarizing checks performed, evidence, results, defects, and recommendations. Output is suitable for `capsule/<feature_id>/reports/validation_report-<YYYY-MM-DD>.md`.

Inputs Required
- feature_id (kebab-case)
- owner (team or human)
- Test plan or acceptance criteria
- Execution logs or evidence sources

Follow-up Rule
- Ask up to 3 clarifying questions. Record unresolved items in “UNKNOWN Summary”.

Generation Instructions
- Schema `$id` base: `urn:automatr:schema:capsule:<feature_id>:quality.validation_report:v<major>`
- SemVer: use SemVer 2.0.0 for `version`.
- Output document header fields:
  - `feature_id: <feature-id>`
  - `owner: <team-or-person>`
  - `doc_type: quality.validation_report`
  - `schema_ref: urn:automatr:schema:capsule:<feature_id>:quality.validation_report:v1@<version>`
  - `version: <semver>`
  - `updated: <YYYY-MM-DD>`

- Sections and schemas:
  - `## Summary`
  - `## Context`
  - `## Method`
  - `## Checks Performed`
    - Table: `ID | Check | Method | Result (Pass/Fail) | Evidence | Ticket/Link`
  - `## Results`
  - `## Defects`
    - Table: `ID | Title | Severity | Status | Owner | Link`
  - `## Recommendations`
  - `## Sign-off`
    - Table: `Role | Name | Decision (Approve/Block) | Date | Notes`
  - `## UNKNOWN Summary`
    - Table: `Field | Context | Owner | Next Step`

Output Requirement
- Output only the document body. Append an HTML comment at the end logging size: `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields valid and complete.
- Checks Performed table contains at least 5 checks or rationale if fewer.
- Any failing checks have corresponding defects or justification.
- Sign-off section present (may be “Pending”).
- UNKNOWN Summary included if open items remain.
- Ends with size log comment.

