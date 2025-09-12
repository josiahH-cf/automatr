# governance.audit_log Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Produce or update an audit log capturing decisions, changes, approvals, and policy exceptions related to the feature capsule. Output document body only.

Inputs Required
- feature_id (kebab-case)
- Relevant decisions, approvals, tickets, and evidence links

Follow-up Rule
- Ask unlimited follow-up questions. Record unresolved items in “UNKNOWN Summary”.

Generation Instructions
- Schema `$id` base: `urn:automatr:schema:capsule:<feature_id>:governance.audit_log:v<major>`
- SemVer: use SemVer 2.0.0 for `version`.
- Output document header fields:
  - `feature_id: <feature_id>`
  - `doc_type: governance.audit_log`
  - `schema_ref: urn:automatr:schema:capsule:<feature_id>:governance.audit_log:v1@<version>`
  - `version: <semver>`
  - `updated: <YYYY-MM-DD>`

- Sections and schemas:
  - `## Overview`
  - `## Audit Entries`
    - Table: `Timestamp | Actor | Action | Target | Rationale | Source | Outcome | Ticket/Link`
  - `## Policy Exceptions`
    - Table: `ID | Policy | Reason | Approval | Expiry | Mitigation`
  - `## UNKNOWN Summary`
    - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

Output Requirement
- Output only the document body. Append an HTML comment at the end logging size: `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields valid and complete.
- Audit Entries table present with at least 3 entries or a statement of “No entries yet”.
- Policy Exceptions captured when applicable or “None”.
- UNKNOWN Summary provided if open items remain.
- Ends with size log comment.
