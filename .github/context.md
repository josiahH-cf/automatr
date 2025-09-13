<!--
Human-only context for this repository. Guidance for AI assistants (Copilot/Codex/others):

- Do NOT treat this file as a prompt or template; it is reference only.
- Do NOT copy or inject any sentences from this file into generated documents.
- Do NOT introduce headers like `feature_id:`, `doc_type:`, `schema_ref:`, `version:`, `updated:` in other files based on this file.
- Do NOT add meta-prompt text (e.g., "You are ...") into any docs under `features/**` or `capsule/**`.
- Authoritative behaviors live in:
  - `prompts/README.md`, `prompts/registry.json`, `prompts/run_capsule_chain.md`
  - `capsule/reports/validation/validate_all.sh` (+ checks under `capsule/reports/validation/`)
  - `tools/final_bundle/README.md` and `tools/final_bundle/verify_and_package.*`
- Validators only scan `features/**` and `capsule/**`; this file is outside those paths and is ignored by gates.
- Maintainers may freely edit this file; keep links current. If you need to move it, prefer `docs/`.
-->

# Editing safety (human note)

This document is intentionally outside `features/**` and `capsule/**` so it won’t affect validators or packaging. If you paste snippets from here into generated docs, remove any meta narrative and keep to the repo’s header/URN rules.

Here’s a drop-in **project context** doc you can paste into your repo as `docs/context.md` (or similar). It’s comprehensive but intentionally **project-agnostic**—you can swap templates, policies, or even the repo without breaking it.

---

# Feature Capsule Engine — Context & Operating Guide

**Last updated:** 2025-09-13 (America/Chicago)
**Scope:** End-to-end scaffolding for planning/governance/quality *documents* (“feature capsules”) and their packaging. No application code is generated.

## 1) Purpose (at a glance)

* Provide a repeatable **pattern** to capture a feature from vision → tests → bundle using a fixed sequence of docs, hard validation gates, and a final packaging step.
* Keep it **environment/project-agnostic**: policy is configurable, validators are pluggable, and templates can be overlaid per repo.

### What this is

* A **spec** (required docs, headers, URNs, size/gating rules).
* An **engine** (controller + validators + bundler).
* A light **adapter layer** (templates/registry/forbidden patterns per repo).

### What this is not

* It does **not** generate application features or code.
* It does **not** call external services/network by default.

---

## 2) Minimal runtime assumptions

* **Shell:** POSIX `sh` (bundler) and `bash` (validator orchestration).
* **Python:** 3.8+ for validators/utilities.
* **No network required** for core flows.
* Works on Linux/macOS; avoid OS-specific paths.
* Optional tools detected at runtime: `git` (for commit), `sha256sum`/`shasum`.

---

## 3) Vocabulary & data contracts

### 3.1 Feature capsule

A folder `features/<feature_id>/` containing a standard set of docs plus `reports/` with structured logs.

### 3.2 Headers (must appear at the top of generated Markdown docs)

```
feature_id: <kebab-case-id>
doc_type: <namespace.slug>           # e.g., planning.vision
schema_ref: urn:automatr:schema:capsule:<feature_id>:<doc_type>:v<MAJOR>@<SEMVER>
version: <SEMVER>                    # e.g., 0.1.0
updated: <YYYY-MM-DD>
```

* **Namespaces:** `planning.*`, `governance.*`, `quality.*`.
* Each doc body includes a standardized **UNKNOWN Summary** table with columns:
  `ID | Question | Possible Effects | Recommended Actions | Next Step | Impact`.

### 3.3 Output contract (per feature)

`features/<feature_id>/output_contract.schema.json` is the **source of truth** for `required` keys, `properties`, and concurrency targets.
Manual tests and acceptance mapping **mirror** this schema.

---

## 4) Canonical document sequence

Order is enforced; validation runs between steps.

1. `vision.md`
2. `exploration.md`
3. `intent_card.md`
4. `output_contract.schema.json`
5. `action_budget.md`
6. `concurrency_model.md`
7. `sync_policies.md`
8. `reference_set.md`
9. `assumptions.md`
10. `evaluation_and_tripwires.md`
11. `meta_prompts.md`
12. `test_plan.md`
13. `runtime_concurrency_tests.md`
14. `observability_slos.md`
15. `reports/manual_tests.md`
16. `reports/chaos_results.md`
17. `audit_log.md`
18. `changelog_entry`
19. `validation_report.md`
20. `phase_transition.md`

> Tip: If a doc footer names the next `doc_type`, prefer that; otherwise fall back to this sequence.

---

## 5) Repository layout (conventional)

* `prompts/` — Template library; `registry.json` maps `doc_type → template`.
* `capsule/` — Program reports (`capsule/reports/**`) and validator scripts (`capsule/reports/validation/**`).
* `features/` — One subfolder per `features/<feature_id>/` with `reports/` for logs.
* `tools/final_bundle/` — Packaging scripts (`verify_and_package.sh` + Python fallback).
* `final_feature_documents/` — Output bundles (created by packager).
* `schemas/` — JSON Schemas (e.g., `bundle_manifest.schema.json`).
* `docs/` — Human docs (usage notes, this context doc, etc).

---

## 6) Validation workflow (between every step)

### 6.1 Per-step validate

```sh
FEATURE_ID=<feature_id> \
DOC_PATH=<path/to/doc-or-schema> \
STEP=<n> \
[DECISIONS="<key notes>"] \
[LINKS="<path or URL>"] \
bash capsule/reports/validation/validate_all.sh
```

**Gates & checks (non-exhaustive):**

* Headers present; `schema_ref` URN canonical for feature/doc/version.
* `prompts/registry.json` round-trip (doc\_type ↔ template).
* Acceptance ↔ `schema.required` mapping (if required keys exist).
* Concurrency tuple present/consistent across docs & schema.
* Forbidden text/leakage blocked; size policy enforced.

**Outcomes:**

* `PASS` → proceed.
* `WARN` → proceed and append entry to `features/<id>/reports/creation_run.md`.
* `FAIL` → stop and surface `STOP/NEED` messages.

### 6.2 Size & forbidden-text policy

* Soft alert around **\~800 tokens** (warn).
* Hard threshold around **\~1600 tokens** (fail unless explicitly approved).
  To override after approval:

  ```sh
  VALIDATION_ALLOW_HARD_SIZE=1 bash capsule/reports/validation/validate_all.sh
  ```
* **Token counting strategy:** configurable. Default is a word→token heuristic. Swap with a true tokenizer when desired.

### 6.3 Schema evolution & dependent sync

If new constraints/fields emerge while drafting:

```sh
python3 capsule/reports/validation/bump_schema_and_sync.py \
  --feature-id <feature_id> \
  --bump {patch|minor|major} \
  --note "<why>" \
  --run-validate
```

Then refresh dependents (acceptance mapping in `intent_card.md`, `action_budget.md`, manual tests, concurrency docs) and re-run validation.

### 6.4 Full-tree validation & IMPLEMENTABLE gating

```sh
FEATURE_ID=<feature_id> bash capsule/reports/validation/validate_all.sh
FEATURE_ID=<feature_id> REQUIRE_IMPLEMENTABLE=1 bash capsule/reports/validation/validate_all.sh
```

* With `REQUIRE_IMPLEMENTABLE=1`, **WARN → FAIL** globally.
* On clean pass, validator marks **IMPLEMENTABLE** and logs the status/date.

---

## 7) Packaging workflow

### 7.1 Preferred (POSIX shell)

```sh
tools/final_bundle/verify_and_package.sh feature_id=<feature_id> [allow_gt_1600_tokens=yes|no]
```

### 7.2 Fallback (Python)

```sh
python3 tools/final_bundle/verify_and_package.py <feature_id> --allow-gt-1600-tokens <yes|no>
```

**Packager enforces hard gates:**

* Required files present (vision/exploration/intent card/schema/etc.).
* Headers and canonical `schema_ref` URN valid.
* Acceptance ↔ `schema.required` complete.
* Concurrency tuple present/consistent.
* No forbidden prompt leakage.
* No High-impact UNKNOWNs.

**Outputs:**

* `final_feature_documents/<feature_id>-<SCHEMA_SEMVER>-<DATE>-<COMMIT>/`
* `manifest.json` (hashes, versions, policy digests) + `SUMMARY.txt`.
* Success line printed with final doc path; verification record appended to the verification log.

---

## 8) Portability model (how this stays repo-agnostic)

### 8.1 Single portable project config

Add a small config at repo root (TOML/YAML/JSON; your choice). Example:

```toml
# capsule.project.toml (example)
spec_version = "1.0.0"

[paths]
templates = ["prompts/"]
registry  = ["prompts/registry.json"]
forbidden = ["capsule/forbidden_patterns.txt"]

[doc_sequence]
# Override or extend as needed; omit to use default sequence.

[token_policy]
strategy       = "word-heuristic"   # or "tiktoken:<model>"
warn_at        = 800
fail_at        = 1600
include_header = true

[validators]
required = ["headers","registry","acceptance_schema","concurrency","leak_and_size","unknowns"]
optional = []

[packaging]
hash_algo = "sha256"
tz        = "UTC"

[engine]
no_network = true
```

**Resolution rules:**

* Search paths layer: **engine defaults → global profile (\~/.capsule) → repo overlay → feature-local**.
* Registry merges (overlay can replace/add); forbidden patterns union; policies last-writer-wins.

### 8.2 Stable CLI façade (optional wrapper)

Expose a consistent CLI even if internals are Bash/Python:

```
capsule create <feature_id>
capsule generate --feature <id> --step <doc_type|auto>
capsule validate --feature <id> [--require-implementable] [--doc <path>]
capsule package  --feature <id> [--allow-gt-tokens yes|no]
capsule info     # prints resolved config & search paths
```

### 8.3 Pluggable validators (protocol suggestion)

* **Inputs:** env (`FEATURE_ID`, `DOC_PATH`, `STEP`, `CAPSULE_CONFIG`).
* **Exit codes:** `0 = OK/WARN`, `1 = FAIL`.
* **Machine line:** each validator prints one JSON line, then any human text, e.g.
  `{"check":"headers","gate":"WARN","summary":"missing schema_ref version"}`
* **Registration:** simple manifest or `validators.d/` directory.

---

## 9) Provenance & observability

* Log every per-step gate result to `features/<id>/reports/creation_run.md` (step, gate, decisions, links).
* Include in the bundle manifest: merged registry digest, validator set + versions, token policy, spec version, and content hashes.
* Keep validator temp files under `.capsule/` (git-ignored).

---

## 10) Quickstart (new feature)

1. Choose a **kebab-case** `feature_id` (3–50 chars).
2. Create:

   ```
   features/<feature_id>/
   features/<feature_id>/reports/
   ```
3. Generate `vision.md` from the template; include headers exactly.
4. **Validate per-step** (see §6.1).
5. Proceed through the **sequence** (§4), evolving the schema and syncing dependents when constraints change (§6.3).
6. Run **full-tree validation**; optionally enforce **IMPLEMENTABLE** (§6.4).
7. **Package** into a final bundle (§7).

---

## 11) Policy knobs you’re expected to tune

* Token thresholds and tokenizer strategy.
* Forbidden patterns (append regex lines; keep false positives low).
* Which WARNs are “elevatable” under `REQUIRE_IMPLEMENTABLE=1` (defaults to all).
* Required vs optional validators per repo.

---

## 12) Open decisions (fill these in for your repo)

* Preferred config format: `TOML | YAML | JSON`: `___`
* Default tokenizer strategy: `___`
* CI policy (what runs on PRs, branch protections): `___`
* Minimal OS support (Linux/macOS/both): `___`
* Where to store approval for >1600-token docs (PR comment/commit message/etc.): `___`
* Validator registration method (`validators.d/manifest` vs config list): `___`

---

## 13) Safety & security notes

* Keep secrets out of templates and generated docs; validators should block obvious prompt/meta-prompt leakage.
* No network access is assumed; if you enable it, declare and review provider/model/rate limits explicitly.

---

## 14) Change log convention

* Maintain `features/<feature_id>/CHANGELOG.md` with one line per gate change or schema bump.
* Implementable transitions append a dated marker to the creation run log.

---

### Appendix: Minimal header snippets

**Markdown doc header (copy-paste):**

```markdown
feature_id: <feature-id>
doc_type: planning.vision
schema_ref: urn:automatr:schema:capsule:<feature-id>:planning.vision:v1@0.1.0
version: 0.1.0
updated: 2025-09-13
```

**UNKNOWN Summary row (example):**

```
U-001 | What is the canonical user identifier? | Mismatched merges | Define `user_id` and boundary | Clarify in schema & action budget | High
```

---

**Use this document as the single source of onboarding context.**
When you tweak policies or add doc\_types/validators, update §8 (config), §6 (validation), and §7 (packaging) accordingly so it remains portable across projects and repos.
<!--
Human-only context for this repository. Guidance for AI assistants (Copilot/Codex/others):

- Do NOT treat this file as a prompt or template; it is reference only.
- Do NOT copy or inject any sentences from this file into generated documents.
- Do NOT introduce headers like `feature_id:`, `doc_type:`, `schema_ref:`, `version:`, `updated:` in other files based on this file.
- Do NOT add meta-prompt text (e.g., "You are ...") into any docs under `features/**` or `capsule/**`.
- Authoritative behaviors live in:
  - `prompts/README.md`, `prompts/registry.json`, `prompts/run_capsule_chain.md`
  - `capsule/reports/validation/validate_all.sh` (+ checks under `capsule/reports/validation/`)
  - `tools/final_bundle/README.md` and `tools/final_bundle/verify_and_package.*`
- Validators only scan `features/**` and `capsule/**`; this file is outside those paths and is ignored by gates.
- Maintainers may freely edit this file; keep links current. If you need to move it, prefer `docs/`.
-->

# Editing safety (human note)

This document is intentionally outside `features/**` and `capsule/**` so it won’t affect validators or packaging. If you paste snippets from here into generated docs, remove any meta narrative and keep to the repo’s header/URN rules.
