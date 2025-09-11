# governance.assumptions Template

Purpose
- Guide a future LLM to populate the capsule’s assumptions and unknowns document. The output must overwrite or update `capsule/<feature_id>/assumptions.md` using the exact header and table schemas below.

Inputs Required
- feature_id (kebab-case)
- owner (team or human)
- Any known assumptions, constraints, or open questions from planning documents

Follow-up Rule
- Ask up to 3 clarifying questions. Record unresolved items in the Unknowns table and in the “UNKNOWN Summary”.

Generation Instructions
- Schema `$id` base: `urn:automatr:schema:capsule:<feature_id>:governance.assumptions:v<major>`
- SemVer: use SemVer 2.0.0 for `version`.
- Output document must start with the exact header and tables:

```
feature_id: <feature-id>
owner: <team-or-person>
doc_type: governance.assumptions
schema_ref: urn:automatr:schema:capsule:<feature_id>:governance.assumptions:v1@<version>
version: <semver>
updated: <YYYY-MM-DD>

## Assumptions
ID | Statement | Confidence | Source/Justification

## Unknowns
ID | Question | Impact | Owner | Next Step | Due
```

Output Requirement
- Output only the document body above, fully populated. Append an HTML comment at the end logging size: `<!-- size: ~<words> words, ~<tokens> tokens -->`.

Acceptance Checklist
- Header fields present and valid (feature_id regex, doc_type fixed, schema_ref URN, SemVer version, updated).
- At least one Assumption or an explicit “None known”.
- Unknowns captured as rows when present.
- Size log comment present.

