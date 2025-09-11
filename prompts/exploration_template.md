# planning.exploration Template

Purpose
- Guide a future LLM to create an exploration document that defines scope, objectives, assumptions, dependencies, risks, and concurrency/scale context for a feature capsule. The output must be a standalone document body suitable for `capsule/<feature_id>/reports/exploration.md`.

Inputs Required
- feature_id (kebab-case, 3–50 chars; optional `-vN` for parallel incompatible capsules)
- owner (team or human)
- Any upstream intent summary if available (e.g., intent_card)
- Known constraints, dependencies, and business context

Follow-up Rule
- Ask up to 3 deep, clarifying questions if inputs are insufficient. If any remain unresolved, record them in the final document under “UNKNOWN Summary” (Field | Context | Owner | Next Step).

Generation Instructions
- Schema `$id` base pattern: `urn:automatr:schema:capsule:<feature_id>:planning.exploration:v<major>`
- SemVer: use SemVer 2.0.0 for the `version` field (e.g., `0.1.0`, pre-release like `-rc.1` allowed).
- Output document must begin with the following header fields exactly:
  - `feature_id: <feature-id>`
  - `owner: <team-or-person>`
  - `doc_type: planning.exploration`
  - `schema_ref: urn:automatr:schema:capsule:<feature_id>:planning.exploration:v1@<version>`
  - `version: <semver>`
  - `updated: <YYYY-MM-DD>`

- Then include the sections below with the exact headings and table schemas:
  - `## Overview`
    - Summary of the problem, intent, and constraints.
  - `## Scope`
    - `### In Scope`
    - `### Out of Scope`
  - `## Objectives and Non-Goals`
  - `## Stakeholders and Consumers`
  - `## Dependencies`
    - Table: `ID | Name | Type | Criticality | Notes`
  - `## Constraints`
  - `## Assumptions`
    - Table: `ID | Statement | Confidence | Source/Justification`
  - `## Risks`
    - Table: `ID | Description | Likelihood | Impact | Mitigation | Owner`
  - `## Concurrency and Scale Characteristics`
  - `## Milestones and Phases`
  - `## Open Questions`
    - Table: `ID | Question | Status | Owner | Due`
  - `## UNKNOWN Summary`
    - Table: `Field | Context | Owner | Next Step`
  - `## References`

Output Requirement
- Output only the document body described above (no prompt text). Append an HTML comment at the end logging approximate size: `<!-- size: ~<words> words, ~<tokens> tokens -->` (estimate tokens if necessary).

Acceptance Checklist
- Header fields present and valid (feature_id regex, doc_type fixed, schema_ref URN pattern, SemVer version, updated date).
- All required sections exist and are non-empty (or explicitly state “None”).
- Tables match the specified column schemas.
- At least one item in Assumptions and Risks or an explicit statement that none are known.
- UNKNOWN Summary table present when any unresolved questions remain.
- Ends with size log comment.

