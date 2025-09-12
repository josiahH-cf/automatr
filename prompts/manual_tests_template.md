# quality.manual_tests Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Generate and maintain manual tests in strict sync with the live schema and acceptance checklist. Derive tests automatically from `planning.intent_card` Acceptance and from `planning.output_contract.schema.json.required`.

Header (for generated doc)
```
feature_id: <feature_id>
doc_type: quality.manual_tests
schema_ref: urn:automatr:schema:capsule:<feature_id>:quality.manual_tests:v1@0.1.0
version: 0.1.0
updated: <YYYY-MM-DD>
```

Sync Rules
- Single source of truth: `/features/<feature_id>/output_contract.schema.json`.
- Ask unlimited follow-up questions if acceptance items or schema details are unclear. Do not fabricate; derive or ask.
- When the schema’s `required` keys change or acceptance items change, update this file immediately and re-run validation.

Sections
- `## Schema Reference`
  - `Contract: urn:automatr:schema:capsule:<feature_id>:planning.output_contract:v1@<version>`
- `## Tests`
  - Table (derive a row per required key; add more as needed):
    `ID | Test Name | Inputs | Expected Result | Linked Schema Key | Status`
- `## Acceptance-to-Test Mapping`
  - Table: `Acceptance Item | Test IDs`
- `## UNKNOWN Summary`
  - Table: `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)`

Logging
- Append each run to `/features/<feature_id>/reports/manual_tests.md` with:
  `Run Date | Version | Pass/Fail Counts | Notes | Links to Artifacts`
- On any failure, add an UNKNOWN Summary item with `Impact = High` and link to evidence.

UNKNOWN Handling
- Log unresolved items into `/features/<feature_id>/assumptions.md` and echo them in this document’s UNKNOWN Summary.

Footer Pointer
- Append one-line footer: `Next doc_type: quality.runtime_concurrency_tests`.
