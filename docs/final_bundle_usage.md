# Final Bundle Usage

This document explains how to verify a single feature capsule and produce a delivery bundle for handoff to an LLM.

Prereqs
- A populated feature capsule under `/features/<feature_id>/`.
- Validation scripts at `capsule/reports/validation/` (already provided in this repo).

Run (shell preferred)
```
tools/final_bundle/verify_and_package.sh feature_id=<kebab-id> [allow_gt_1600_tokens=yes|no]
```

Fallback (Python)
```
python3 tools/final_bundle/verify_and_package.py <kebab-id> --allow-gt-1600-tokens <yes|no>
```

What happens
- Hard gates are checked (identity, acceptance↔required, concurrency tuple, leakage/forbidden, size, unknowns, nothing-breaks).
- On PASS, a bundle is created at `/final_feature_documents/<feature_id>-<SCHEMA_SEMVER>-<DATE>-<COMMIT>/`.
- `manifest.json` and `SUMMARY.txt` are added; a record line is appended to `capsule/reports/final_bundle_verification.md`.

Exit behavior
- On hard STOP, the script prints a STOP/NEED/PATHS block and exits non-zero. No bundle is created.
- On success, prints exactly the success line with the final doc path.

