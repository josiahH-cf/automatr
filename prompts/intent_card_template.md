# planning.intent_card Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Guide generation of an intent card summarizing problem, value hypothesis, personas, success metrics, non‑goals, and acceptance criteria. Output is a standalone document body.

Inputs Required
- feature_id (kebab-case)
- Business/strategic context and target outcomes (if available)
- Any prior exploration notes if available

Follow-up Rule
- Ask unlimited follow-up questions. Record unresolved items in “UNKNOWN Summary”.

Generation Instructions
- Schema `$id` base: `urn:automatr:schema:capsule:<feature_id>:planning.intent_card:v<major>`
- SemVer: use SemVer 2.0.0 for `version`.
- Output document header fields (exact, no owner):
  - `feature_id: <feature_id>`
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
  - `## Checklist ↔ Schema Mapping`
    - Table: `Checklist Item | Required Schema Key`
  - `## Concurrency Targets`
    - Table: `Throughput (rps) | Latency p50 (ms) | Latency p95 (ms) | Latency p99 (ms) | Error Budget (%) | Window (days)`
  - `## Assumptions`
  - `## Risks`
  - `## Dependencies`
  - `## UNKNOWN Summary`
    - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: planning.output_contract`.
  - `## References`

Output Requirement
- Output only the document body. Append an HTML comment at the end logging approximate size: `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields valid (feature_id regex, fixed doc_type, correct schema_ref URN, SemVer version, updated date).
- Clear problem statement and value hypothesis.
- Success Metrics table provided with targets and sources.
- Acceptance Criteria listed and testable.
- Checklist ↔ Schema Mapping present when `required` keys exist.
- Concurrency Targets present with consistent units (rps, ms, %, days).
- UNKNOWN Summary present if unresolved items exist.
- Ends with size log comment.
