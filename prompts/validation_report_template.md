# quality.validation_report Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Produce a validation report summarizing checks performed, evidence, results, defects, and recommendations. Output document body only.

Inputs Required
- feature_id (kebab-case)
- Test plan or acceptance criteria
- Execution logs or evidence sources

Follow-up Rule
- Ask unlimited follow-up questions. Record unresolved items in “UNKNOWN Summary”.

Generation Instructions
- Schema `$id` base: `urn:automatr:schema:capsule:<feature_id>:quality.validation_report:v<major>`
- SemVer: use SemVer 2.0.0 for `version`.
- Output document header fields:
  - `feature_id: <feature_id>`
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
    - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

Output Requirement
- Output only the document body. Append an HTML comment at the end logging size: `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields valid and complete.
- Checks Performed table contains at least 5 checks or rationale if fewer.
- Any failing checks have corresponding defects or justification.
- Sign-off section present (may be “Pending”).
- UNKNOWN Summary included if open items remain.
- Ends with size log comment.
