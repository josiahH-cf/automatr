# governance.assumptions Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Populate the capsule’s assumptions and unknowns document. Output must use the exact header and table schemas below.

Inputs Required
- feature_id (kebab-case)
- Any known assumptions, constraints, or open questions from planning documents

Follow-up Rule
- Ask unlimited follow-up questions. Record unresolved items in the Unknowns table and in the “UNKNOWN Summary”.

Generation Instructions
- Schema `$id` base: `urn:automatr:schema:capsule:<feature_id>:governance.assumptions:v<major>`
- SemVer: use SemVer 2.0.0 for `version`.
- Output document must start with the exact header and tables:

```
feature_id: <feature_id>
doc_type: governance.assumptions
schema_ref: urn:automatr:schema:capsule:<feature_id>:governance.assumptions:v1@<version>
version: <semver>
updated: <YYYY-MM-DD>

## Assumptions
ID | Statement | Confidence | Source/Justification

## UNKNOWN Summary
ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)
```

Output Requirement
- Output only the document body above, fully populated. Append an HTML comment at the end logging size: `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields present and valid (feature_id regex, doc_type fixed, schema_ref URN, SemVer version, updated).
- At least one Assumption or an explicit “None known”.
- Unknowns captured as rows when present.
- Size log comment present.

Footer Pointer
- Append one-line footer: `Next doc_type: governance.evaluation_and_tripwires`.
