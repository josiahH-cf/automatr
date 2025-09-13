# Phase 4 Validation & Workflow Report

Path: capsule/reports/phase4_validation.md

**Overview**
- Date: 2025-09-11
- Repo Base Commit: aa99846a590d321ee4507aa9523a5813dd5b4a96
- Mission: Add baseline validation automation and document a worked example for creating a new capsule using the prompt templates. No product features are included; this strengthens scaffolding and safety for future meta-prompts and LLMs.

**Validation Automation**
- Location: `capsule/reports/validation/`
- Checks implemented (language/runtime noted):
  - `check_feature_id.sh` (bash)
    - Enforces `feature_id` regex: `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:-v[0-9]+)?$`.
    - Usage: `capsule/reports/validation/check_feature_id.sh billing-refunds-v2`
  - `check_semver.sh` (bash)
    - Validates SemVer 2.0.0 including optional pre-release and build metadata.
    - Usage: `capsule/reports/validation/check_semver.sh 1.2.3-rc.1+build.5`
  - `check_registry.py` (python3)
    - Verifies that every `doc_type` in `prompts/registry.json` maps to an existing template file and that every `*_template.md` under `prompts/` is present in the registry.
    - Also enforces `doc_type` namespace to one of `planning.*`, `governance.*`, `quality.*`.
    - Usage: `python3 capsule/reports/validation/check_registry.py`
  - `check_document_headers.py` (python3)
    - Validates generated document headers for required fields and formats:
      - `feature_id`, `owner`, `doc_type`, `schema_ref`, `version`, `updated`.
      - `feature_id` regex, `doc_type` namespace, `version` SemVer, `updated` date `YYYY-MM-DD`.
      - `schema_ref` pattern: `urn:automatr:schema:capsule:<feature_id>:<doc_type>:v<major>@<version>` and cross-field equality checks.
    - Usage: `python3 capsule/reports/validation/check_document_headers.py <path/to/doc.md>`
  - `validate_all.sh` (bash)
    - Orchestrates registry check and validates all documents that contain a `doc_type:` header under `capsule/`.
    - Usage: `bash capsule/reports/validation/validate_all.sh`
- CI Hook Guidance
  - Recommended: run `check_registry.py` and `validate_all.sh` on every PR.
  - Runtime: bash + Python 3.8+ (no network required).
  - Exit codes: non-zero exit signals validation failure.

**Example Capsule Workflow**
1) Choose feature_id
   - Pick kebab-case ID (3–50 chars). Example: `billing-refunds-v2` (only if a parallel, incompatible capsule must coexist; otherwise use stable ID without `-vN`).
   - Validate: `capsule/reports/validation/check_feature_id.sh billing-refunds-v2`.

2) Scaffold capsule folders
   - Create directories:
     - `capsule/billing-refunds-v2/`
     - `capsule/billing-refunds-v2/reports/`
   - Seed files (copy from placeholders or regenerate via templates later):
     - `capsule/billing-refunds-v2/assumptions.md`
     - `capsule/billing-refunds-v2/CHANGELOG.md`

3) Generate planning.exploration
   - Prompt: use `prompts/exploration_template.md` with inputs: `feature_id`, `owner`, constraints, context.
   - Output target: `capsule/billing-refunds-v2/reports/exploration.md`.
   - Validate header: `python3 capsule/reports/validation/check_document_headers.py capsule/billing-refunds-v2/reports/exploration.md`.
   - Resolve UNKNOWNs: capture in `UNKNOWN Summary` and carry open items forward.

4) Generate planning.intent_card
   - Prompt: `prompts/intent_card_template.md` (use exploration outputs as inputs).
   - Output: `capsule/billing-refunds-v2/reports/intent_card.md`.
   - Validate header: run header check script.

5) Update governance.assumptions
   - Prompt: `prompts/assumptions_template.md` to populate `capsule/billing-refunds-v2/assumptions.md`.
   - Ensure header fields exist (now includes `doc_type` and `schema_ref`).
   - Validate header: run header check script.

6) Create quality.test_plan
   - Prompt: `prompts/test_plan_template.md` (inputs: intent/exploration, environments, data).
   - Output: `capsule/billing-refunds-v2/reports/test_plan-<YYYY-MM-DD>.md`.
   - Validate header and required sections; update as needed.

7) Produce quality.validation_report
   - Prompt: `prompts/validation_report_template.md` using executed checks/evidence.
   - Output: `capsule/billing-refunds-v2/reports/validation_report-<YYYY-MM-DD>.md`.
   - Validate header; ensure failing checks map to defects.

8) Maintain governance.audit_log
   - Prompt: `prompts/audit_log_template.md` to create/update `capsule/billing-refunds-v2/reports/audit_log.md`.
   - Record decisions, approvals, and exceptions.

9) Record CHANGELOG entries
   - Prompt: `prompts/changelog_entry_template.md` to generate a single line.
   - Append to `capsule/billing-refunds-v2/CHANGELOG.md`.
   - SemVer policy:
     - PATCH for clarifications/fixes to docs.
     - MINOR for additive, backward-compatible sections/criteria.
     - MAJOR if schema or documented contracts break.
   - Validate version string: `capsule/reports/validation/check_semver.sh <version>`.

10) Run validations
   - `python3 capsule/reports/validation/check_registry.py`
   - `bash capsule/reports/validation/validate_all.sh`
   - Address any errors; iterate until clean.

11) Provenance
   - Capture the current commit hash (e.g., `git rev-parse HEAD`) and record it in phase reports or document footers as needed.

**UNKNOWN Summary**
| Field | Context | Suggested Owner | Next Step |
| --- | --- | --- | --- |
| CI environment | Preferred CI (e.g., GitHub Actions) and runtime versions are not specified. | Repo Maintainer | Confirm CI platform and ensure bash + Python 3.8+ are available. |
| Template evolution policy | How to version template schema majors (`v<major>`) across many capsules is not formalized. | Architecture/Platform Owner | Define policy for when to bump `v<major>` in `$id` and communicate baseline. |
| Report naming conventions | Whether to enforce ISO dates in report filenames (e.g., `test_plan-YYYY-MM-DD.md`) across all reports. | Documentation/Platform Owner | Approve standard and add to a linter or rename guidance. |

**Notes**
- Token size: Templates target ~800 tokens; if a generated document diverges substantially, the templates instruct models to flag and propose split/condense.
- Dependencies: Validation scripts require bash and Python 3.8+; no network access is needed.

