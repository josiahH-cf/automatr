# Phase 2 Scaffold Report

Path: capsule/reports/phase2_scaffold.md

**Overview**
- Date: 2025-09-11
- Repo Base Commit: aa99846a590d321ee4507aa9523a5813dd5b4a96
- Mission: Materialize the repository scaffold by creating the placeholder folders, seed files, and prompt registry that future meta-prompts will use to generate documents and feature capsules. No product features are included.

**Folders Created**
- `capsule/` — Root for feature capsules and program reports.
- `capsule/<feature_id>/` — Feature-scoped workspace (literal placeholder; future runs replace with kebab-case ID).
- `capsule/<feature_id>/reports/` — Per-feature validation, test, and audit artifacts.
- `capsule/reports/` — Program/phase reports (this file lives here).
- `prompts/` — Global prompt library root.

**Files Created**
- `capsule/<feature_id>/assumptions.md` — Seed header and empty table stubs for assumptions and unknowns.
- `capsule/<feature_id>/CHANGELOG.md` — Initial changelog entry for the capsule initialization.
- `prompts/registry.json` — Mapping of `doc_type` slugs to prompt template paths.

**Seed File Contents (exact)**
- `capsule/<feature_id>/assumptions.md`
```
feature_id: <feature-id>
owner: <team-or-person>
version: 0.1.0
updated: <YYYY-MM-DD>
schema_ref: <schema-id>@<version>

## Assumptions
ID | Statement | Confidence | Source/Justification

## Unknowns
ID | Question | Impact | Owner | Next Step | Due
```

- `capsule/<feature_id>/CHANGELOG.md`
```
YYYY-MM-DD | 0.1.0 | Initialized capsule with seed docs
```

- `prompts/registry.json`
```json
{
  "planning.exploration": "prompts/exploration_template.md",
  "planning.intent_card": "prompts/intent_card_template.md",
  "governance.assumptions": "prompts/assumptions_template.md",
  "governance.changelog_entry": "prompts/changelog_entry_template.md",
  "quality.test_plan": "prompts/test_plan_template.md",
  "quality.validation_report": "prompts/validation_report_template.md",
  "governance.audit_log": "prompts/audit_log_template.md"
}
```

**Naming & Versioning Rules**
- **feature_id**: kebab-case slug, 3–50 chars; lowercase alphanumerics and hyphens; optional `-vN` suffix only when a new, incompatible capsule must coexist with an older one.
- **schema `$id` (canonical)**: `urn:automatr:schema:capsule:<feature_id>:<doc_type>:v<major>`; URL alias may be added later without breaking URN.
- **schema_ref**: placeholder in headers as `<schema-id>@<version>`; future tooling will resolve to the canonical `$id` plus SemVer.
- **version**: SemVer 2.0.0 (`MAJOR.MINOR.PATCH`), supporting pre-release (e.g., `-rc.1`) and build metadata (`+meta`).
- **doc_type namespaces**: `planning.*`, `governance.*`, `quality.*` (stable slugs used as keys in `prompts/registry.json`).

**Prompt Library Map**
- Registry file: `prompts/registry.json`
- Mapping (doc_type → prompt_path): see JSON above. Paths are repo-relative.

**UNKNOWN Summary**
| Field | Context | Owner | Next Step |
| --- | --- | --- | --- |
| N/A | No outstanding unknowns for Phase 2. | — | — |

**Next Action**
- Proceed to Phase 3: author empty prompt templates under `prompts/` to match the registry keys and add any automation scripts for validation (e.g., feature_id regex, SemVer checks). Capture the base commit again upon creation to record provenance.

