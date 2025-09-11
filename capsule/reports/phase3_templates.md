# Phase 3 Prompt Templates Report

Path: capsule/reports/phase3_templates.md

**Overview**
- Date: 2025-09-11
- Repo Base Commit: aa99846a590d321ee4507aa9523a5813dd5b4a96
- Mission: Create initial, self-contained prompt templates for each `doc_type` registered in `prompts/registry.json`. These templates are meta-prompts to guide future models to generate the actual documents; no product features were created.

**Templates Created**
- `prompts/exploration_template.md` — planning.exploration
- `prompts/intent_card_template.md` — planning.intent_card
- `prompts/assumptions_template.md` — governance.assumptions
- `prompts/changelog_entry_template.md` — governance.changelog_entry
- `prompts/test_plan_template.md` — quality.test_plan
- `prompts/validation_report_template.md` — quality.validation_report
- `prompts/audit_log_template.md` — governance.audit_log

**Key Template Conventions**
- **Header fields (in generated docs)**: `feature_id`, `owner`, `doc_type`, `schema_ref`, `version` (SemVer 2.0.0), `updated` (YYYY-MM-DD).
- **Schema `$id` base**: `urn:automatr:schema:capsule:<feature_id>:<doc_type>:v<major>`; `schema_ref` uses this URN plus `@<version>`.
- **SemVer**: MAJOR breaking, MINOR additive, PATCH fixes; pre-release/build metadata allowed.
- **Follow-up rule**: Each template instructs asking up to 3 clarifying questions and recording unresolved items in an `UNKNOWN Summary` table.
- **Output requirement**: When used, the model outputs only the target document body and appends an HTML size log comment at the end.

**File Map Confirmation**
- Registry (`prompts/registry.json`) mappings remain:
  - planning.exploration → `prompts/exploration_template.md`
  - planning.intent_card → `prompts/intent_card_template.md`
  - governance.assumptions → `prompts/assumptions_template.md`
  - governance.changelog_entry → `prompts/changelog_entry_template.md`
  - quality.test_plan → `prompts/test_plan_template.md`
  - quality.validation_report → `prompts/validation_report_template.md`
  - governance.audit_log → `prompts/audit_log_template.md`

**UNKNOWN Summary**
| Field | Context | Owner | Next Step |
| --- | --- | --- | --- |
| Report file naming | Using `phase3_templates.md`. Confirm if alternate naming is preferred. | Repo Maintainer | Approve or request rename. |

**Next Action**
- Phase 4: Wire basic validation automation (feature_id regex, SemVer checks, registry consistency) and provide example generation workflows for a new capsule. Capture the base commit in the Phase 4 report upon creation.
