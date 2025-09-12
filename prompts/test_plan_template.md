# quality.test_plan Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Create a comprehensive test plan covering scope, strategy, environments, data, detailed test cases, non‑functional requirements, tooling, reporting, and traceability. Output document body only.

Inputs Required
- feature_id (kebab-case)
- Intent/Exploration docs if available (to derive scope and criteria)
- Environments, data availability, compliance constraints (if known)

Follow-up Rule
- Ask unlimited follow-up questions. Record unresolved items in “UNKNOWN Summary”.

Generation Instructions
- Schema `$id` base: `urn:automatr:schema:capsule:<feature_id>:quality.test_plan:v<major>`
- SemVer: use SemVer 2.0.0 for `version`.
- Output document header fields:
  - `feature_id: <feature_id>`
  - `doc_type: quality.test_plan`
  - `schema_ref: urn:automatr:schema:capsule:<feature_id>:quality.test_plan:v1@<version>`
  - `version: <semver>`
  - `updated: <YYYY-MM-DD>`

- Sections and schemas:
  - `## Overview`
  - `## Scope`
  - `## Risks & Assumptions`
  - `## Test Strategy`
    - Unit, Integration, E2E, Performance, Security, Accessibility
  - `## Test Environments`
  - `## Test Data`
  - `## Entry Criteria`
  - `## Exit Criteria`
  - `## Test Cases`
    - Table: `ID | Title | Type | Preconditions | Steps | Expected Result | Owner | Priority | Trace ID`
  - `## Non-Functional Requirements`
    - Subsections for Performance, Reliability, Security, Accessibility with targets
  - `## Tooling & Automation`
  - `## Reporting & Metrics`
  - `## Traceability Matrix`
    - Table: `Requirement | Test IDs | Coverage (%) | Notes`
  - `## UNKNOWN Summary`
    - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

Output Requirement
- Output only the document body. Append an HTML comment at the end logging size: `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields valid and complete.
- Test cases table provided with at least 5 representative cases or rationale if fewer.
- Non-functional targets present when applicable.
- Traceability Matrix present or rationale if not applicable yet.
- UNKNOWN Summary included if any open items.
- Ends with size log comment.
