# planning.intent_card Template

Purpose
- Guide a future LLM to create an intent card summarizing the problem, value hypothesis, personas, success metrics, non-goals, and acceptance criteria. The output is a standalone document body suitable for `capsule/<feature_id>/reports/intent_card.md`.

Inputs Required
- feature_id (kebab-case)
- owner (team or human)
- Business/strategic context and target outcomes (if available)
- Any prior exploration notes if available

Follow-up Rule
- Ask up to 3 clarifying questions. Record unresolved items in “UNKNOWN Summary”.

Generation Instructions
- Schema `$id` base: `urn:automatr:schema:capsule:<feature_id>:planning.intent_card:v<major>`
- SemVer: use SemVer 2.0.0 for `version`.
- Output document header fields (exact):
  - `feature_id: <feature-id>`
  - `owner: <team-or-person>`
  - `doc_type: planning.intent_card`
  - `schema_ref: urn:automatr:schema:capsule:<feature_id>:planning.intent_card:v1@<version>`
  - `version: <semver>`
  - `updated: <YYYY-MM-DD>`

- Sections and field schemas:
  - `## Intent Summary`
  - `## Problem Statement`
  - `## Value Hypothesis`
  - `## Personas & Users`
  - `## Success Metrics`
    - Table: `Metric | Target | Data Source | Review Cadence`
  - `## Non-Goals`
  - `## Key Decisions & Tradeoffs`
    - Table: `Decision | Status | Rationale | Date`
  - `## Acceptance Criteria`
    - Provide numbered, testable criteria.
  - `## Assumptions`
  - `## Risks`
  - `## Dependencies`
  - `## UNKNOWN Summary`
    - Table: `Field | Context | Owner | Next Step`
  - `## References`

Output Requirement
- Output only the document body. Append an HTML comment at the end logging approximate size: `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields valid (feature_id regex, fixed doc_type, correct schema_ref URN, SemVer version, updated date).
- Clear problem statement and value hypothesis.
- Success Metrics table provided with targets and sources.
- Acceptance Criteria listed and testable.
- UNKNOWN Summary present if unresolved items exist.
- Ends with size log comment.

