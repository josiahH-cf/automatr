# governance.changelog_entry Template

You are generating scaffolding documents only. Ask unlimited follow‑ups when inference fails. Output the document body only. After each document, run validations; update schema/docs if new answers change constraints; then proceed to the next doc.

Purpose
- Guide a future LLM to generate a single CHANGELOG entry line for `capsule/<feature_id>/CHANGELOG.md` that complies with SemVer and the capsule’s conventions.

Inputs Required
- feature_id (kebab-case)
- Change summary (one line)
- Impact description and rationale (to select version bump)
- Change type (Added/Changed/Fixed/Removed/Deprecated/Security/Docs/etc.)

Follow-up Rule
- Ask unlimited follow-up questions. If unresolved, include a brief note in parentheses at the end of the line and add an item to UNKNOWN Summary (in a separate report if required).

Generation Instructions
- Schema `$id` base: `urn:automatr:schema:capsule:<feature_id>:governance.changelog_entry:v<major>`
- Determine SemVer bump (MAJOR/MINOR/PATCH) based on impact:
  - MAJOR: incompatible or breaking change
  - MINOR: backward-compatible additions
  - PATCH: backward-compatible fixes/clarifications
- Output format (single line, no header):
```
YYYY-MM-DD | <version> | <Change type>: <One-line Change Note>
```
- Keep the note terse; do not modify prior entries.

Output Requirement
- Output ONLY the single line above (no additional text). Keep within ~120 characters if possible.

Acceptance Checklist
- Date in ISO format `YYYY-MM-DD`.
- Version is valid SemVer and consistent with impact.
- Clear change type and concise note.
