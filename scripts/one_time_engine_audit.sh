#!/usr/bin/env bash
set -euo pipefail

ENG_ROOT="tools/capsule-engine"

fail=0
note() { echo "[INFO] $*"; }
err() { echo "[FAIL] $*" >&2; fail=1; }

if [[ ! -d "$ENG_ROOT" ]]; then
  err "Engine folder not found: $ENG_ROOT"; exit 1
fi

# 1) No feature instances in engine capsule (only 'reports' allowed)
if [[ -d "$ENG_ROOT/capsule" ]]; then
  mapfile -t bad < <(find "$ENG_ROOT/capsule" -mindepth 1 -maxdepth 1 -type d ! -name reports)
  if (( ${#bad[@]} > 0 )); then
    err "Found app-specific dirs under engine capsule/: ${bad[*]}"
  else
    note "capsule/ clean (only reports present)"
  fi
else
  note "capsule/ not present (ok)"
fi

# 2) No validation/.run_tmp present
if [[ -d "$ENG_ROOT/capsule/reports/validation/.run_tmp" ]]; then
  err "validation/.run_tmp should not be committed"
else
  note "validation/.run_tmp not present"
fi

# 3) No duplicate packager scripts outside tools/final_bundle/*
if [[ -f "$ENG_ROOT/tools/verify_and_package.sh" || -f "$ENG_ROOT/tools/verify_and_package.py" ]]; then
  err "Duplicate packager scripts found in tools/ (should only exist under tools/final_bundle/)"
else
  note "No duplicate packager scripts in tools/"
fi

# 4) No app-specific namespace strings leaking in engine code (allow docs/templates/tools/validation/prompts/schemas)
AUTO=$(rg -n "automatr" "$ENG_ROOT" -S --hidden \
  -g '!tools/capsule-engine/capsule/reports/validation/**' \
  -g '!tools/capsule-engine/tools/**' \
  -g '!tools/capsule-engine/templates/**' \
  -g '!tools/capsule-engine/.git/**' \
  -g '!tools/capsule-engine/README.md' \
  -g '!tools/capsule-engine/prompts/**' \
  -g '!tools/capsule-engine/schemas/**' || true)
if [[ -n "$AUTO" ]]; then
  err "Found 'automatr' references in engine outside allowed docs:"
  echo "$AUTO" >&2
else
  note "No unexpected 'automatr' references in engine"
fi

if (( fail == 0 )); then
  echo "PASS: engine audit clean"
  exit 0
else
  echo "FAIL: engine audit found issues" >&2
  exit 1
fi

