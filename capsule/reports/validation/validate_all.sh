#!/usr/bin/env bash
# Validation loop with gating and logging
# PASS -> proceed; WARN -> proceed and log; FAIL -> stop
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
VALIDATION_DIR="$(cd "$(dirname "$0")" && pwd)"

FEATURE_ID="${FEATURE_ID:-}"
DOC_PATH="${DOC_PATH:-}"
STEP_LABEL="${STEP:-}"
DECISIONS="${DECISIONS:-}"
LINKS="${LINKS:-}"
REQUIRE_CONCURRENCY="${REQUIRE_CONCURRENCY:-0}"
ALLOW_HARD_SIZE="${VALIDATION_ALLOW_HARD_SIZE:-0}"

TMP_DIR="${VALIDATION_DIR}/.run_tmp"
mkdir -p "$TMP_DIR"
REG_OUT="$TMP_DIR/registry.out"
HDR_OUT="$TMP_DIR/headers.out"
ACC_OUT="$TMP_DIR/acceptance.out"
CON_OUT="$TMP_DIR/concurrency.out"
LEAK_OUT="$TMP_DIR/leaksize.out"
UNK_OUT="$TMP_DIR/unknowns.out"
MTEST_OUT="$TMP_DIR/manualtests.out"
CRUN_OUT="$TMP_DIR/creationrun.out"
UNKB_OUT="$TMP_DIR/unknowns_policy.out"
IMPL_OUT="$TMP_DIR/implementable.out"

GATE="PASS"
WARN_COUNT=0
FAIL_COUNT=0
STOP_REASON=""

echo "== Checking prompts registry =="
set +e
if command -v python3 >/dev/null 2>&1; then
  python3 "$VALIDATION_DIR/check_registry.py" | tee "$REG_OUT"
  rc=$?
elif command -v python >/dev/null 2>&1; then
  python "$VALIDATION_DIR/check_registry.py" | tee "$REG_OUT"
  rc=$?
else
  echo "WARNING: Python not found; skipping registry check" | tee "$REG_OUT" >&2
  rc=0
fi
set -e
if [[ $rc -ne 0 ]]; then
  GATE="FAIL"; ((FAIL_COUNT++))
  STOP_REASON="Registry check failed"
fi

echo "== Validating generated documents (with doc_type) =="
FOUND=0
set +e
> "$HDR_OUT"
while IFS= read -r -d '' file; do
  if grep -q '^doc_type:' "$file"; then
    # Skip placeholder skeletons that use the literal '<feature-id>' or '<feature_id>'
    fid=$(awk -F': ' '/^feature_id:/ {print $2; exit}' "$file")
    if [[ "$fid" == "<feature-id>" || "$fid" == "<feature_id>" || -z "$fid" ]]; then
      echo "SKIP skeleton: $file" | tee -a "$HDR_OUT"
      continue
    fi
    FOUND=1
    if command -v python3 >/dev/null 2>&1; then
      python3 "$VALIDATION_DIR/check_document_headers.py" "$file" | tee -a "$HDR_OUT"
      rc=$?
    else
      python "$VALIDATION_DIR/check_document_headers.py" "$file" | tee -a "$HDR_OUT"
      rc=$?
    fi
    if [[ $rc -ne 0 ]]; then
      GATE="FAIL"; ((FAIL_COUNT++)); [[ -z "$STOP_REASON" ]] && STOP_REASON="Header validation failed in $file"
    fi
  fi
done < <(find "$ROOT_DIR/capsule" -type f -name "*.md" -print0 2>/dev/null)

# Also scan /features/** for generated docs
while IFS= read -r -d '' file; do
  if grep -q '^doc_type:' "$file"; then
    fid=$(awk -F': ' '/^feature_id:/ {print $2; exit}' "$file")
    if [[ -z "$fid" ]]; then continue; fi
    # For features, feature_id should NOT be placeholder
    if [[ "$fid" == "<feature-id>" || "$fid" == "<feature_id>" ]]; then
      echo "WARN placeholder feature_id in $file" | tee -a "$HDR_OUT"
      ((WARN_COUNT++)); [[ "$GATE" == "PASS" ]] && GATE="WARN"
      continue
    fi
    if command -v python3 >/dev/null 2>&1; then
      python3 "$VALIDATION_DIR/check_document_headers.py" "$file" | tee -a "$HDR_OUT"
      rc=$?
    else
      python "$VALIDATION_DIR/check_document_headers.py" "$file" | tee -a "$HDR_OUT"
      rc=$?
    fi
    if [[ $rc -ne 0 ]]; then
      GATE="FAIL"; ((FAIL_COUNT++)); [[ -z "$STOP_REASON" ]] && STOP_REASON="Header validation failed in $file"
    fi
  fi
done < <(find "$ROOT_DIR/features" -type f -name "*.md" -print0 2>/dev/null)
set -e

echo "== Registry round-trip =="
set +e
if command -v python3 >/dev/null 2>&1; then
  python3 "$VALIDATION_DIR/check_registry.py" | tee -a "$REG_OUT"
  rc=$?
else
  python "$VALIDATION_DIR/check_registry.py" | tee -a "$REG_OUT"
  rc=$?
fi
set -e
if [[ $rc -ne 0 ]]; then
  GATE="FAIL"; ((FAIL_COUNT++)); [[ -z "$STOP_REASON" ]] && STOP_REASON="Registry round-trip failed"
fi

echo "== Additional checks (acceptance/schema, concurrency, leakage/size) =="
set +e
if command -v python3 >/dev/null 2>&1; then
  python3 "$VALIDATION_DIR/x_check_acceptance_schema.py" | tee "$ACC_OUT"
  python3 "$VALIDATION_DIR/x_check_concurrency.py" | tee "$CON_OUT"
  python3 "$VALIDATION_DIR/x_check_leak_and_size.py" | tee "$LEAK_OUT"
  python3 "$VALIDATION_DIR/x_list_unknowns.py" | tee "$UNK_OUT"
  python3 "$VALIDATION_DIR/x_check_manual_tests.py" | tee "$MTEST_OUT"
  python3 "$VALIDATION_DIR/x_check_creation_run.py" | tee "$CRUN_OUT"
  python3 "$VALIDATION_DIR/x_check_unknowns_policy.py" | tee "$UNKB_OUT"
  python3 "$VALIDATION_DIR/x_check_implementable.py" | tee "$IMPL_OUT"
fi
set +e

# Derive WARN/FAIL from outputs
if grep -q 'WARN:' "$ACC_OUT" 2>/dev/null; then
  ((WARN_COUNT++)); [[ "$GATE" == "PASS" ]] && GATE="WARN"
fi
if grep -q '^.*: WARN:' "$CON_OUT" 2>/dev/null; then
  ((WARN_COUNT++)); [[ "$GATE" == "PASS" ]] && GATE="WARN"
fi

if grep -q 'FAIL: possible prompt leakage' "$LEAK_OUT" 2>/dev/null; then
  GATE="FAIL"; ((FAIL_COUNT++)); [[ -z "$STOP_REASON" ]] && STOP_REASON="Prompt leakage detected"
fi
if grep -q 'HARD: size very large' "$LEAK_OUT" 2>/dev/null; then
  if [[ "$ALLOW_HARD_SIZE" == "1" ]]; then
    ((WARN_COUNT++)); [[ "$GATE" == "PASS" ]] && GATE="WARN"
  else
    GATE="FAIL"; ((FAIL_COUNT++)); [[ -z "$STOP_REASON" ]] && STOP_REASON="Hard size threshold exceeded (require approval)"
  fi
fi
if grep -q 'SOFT: size large' "$LEAK_OUT" 2>/dev/null; then
  ((WARN_COUNT++)); [[ "$GATE" == "PASS" ]] && GATE="WARN"
fi

# Manual tests alignment gating
if grep -q ': FAIL:' "$MTEST_OUT" 2>/dev/null; then
  GATE="FAIL"; ((FAIL_COUNT++)); [[ -z "$STOP_REASON" ]] && STOP_REASON="Manual tests not aligned with schema/acceptance"
fi
if grep -q ': WARN:' "$MTEST_OUT" 2>/dev/null; then
  ((WARN_COUNT++)); [[ "$GATE" == "PASS" ]] && GATE="WARN"
fi

# Creation run log gating
if grep -q ': FAIL:' "$CRUN_OUT" 2>/dev/null; then
  GATE="FAIL"; ((FAIL_COUNT++)); [[ -z "$STOP_REASON" ]] && STOP_REASON="Creation run log invalid"
fi
if grep -q ': WARN:' "$CRUN_OUT" 2>/dev/null; then
  ((WARN_COUNT++)); [[ "$GATE" == "PASS" ]] && GATE="WARN"
fi

# Unknowns policy and implementable presence/headers
if grep -q ': FAIL:' "$UNKB_OUT" 2>/dev/null; then
  GATE="FAIL"; ((FAIL_COUNT++)); [[ -z "$STOP_REASON" ]] && STOP_REASON="Blocking UNKNOWNs present"
fi
if grep -q ': FAIL:' "$IMPL_OUT" 2>/dev/null; then
  ((FAIL_COUNT++)); GATE="FAIL"; [[ -z "$STOP_REASON" ]] && STOP_REASON="Implementable requirements not met"
fi

set -e

# UNKNOWNs handling: warn if unknowns present but assumptions.md missing for this feature
if [[ -n "$FEATURE_ID" && -s "$UNK_OUT" ]]; then
  if [[ ! -f "$ROOT_DIR/features/$FEATURE_ID/assumptions.md" ]]; then
    ((WARN_COUNT++)); [[ "$GATE" == "PASS" ]] && GATE="WARN"
  fi
fi

if [[ "$FOUND" -eq 0 ]]; then
  echo "Note: No generated documents with 'doc_type:' found yet; header validation skipped."
fi

# Write per-step creation log if feature context provided
if [[ -n "$FEATURE_ID" && -d "$ROOT_DIR/features/$FEATURE_ID" ]]; then
  REPORT_DIR="$ROOT_DIR/features/$FEATURE_ID/reports"
  mkdir -p "$REPORT_DIR"
  LOG_FILE="$REPORT_DIR/creation_run.md"
  TODAY=$(date +%F)
  if [[ ! -f "$LOG_FILE" ]]; then
    {
      echo "feature_id: $FEATURE_ID"
      echo "doc_type: governance.creation_run"
      echo "schema_ref: urn:automatr:schema:capsule:$FEATURE_ID:governance.creation_run:v1@0.1.0"
      echo "version: 0.1.0"
      echo "updated: $TODAY"
      echo
      echo "Step | Doc | Gate | Key decisions | Links"
      echo "--- | --- | --- | --- | ---"
      echo
      echo "## UNKNOWN Summary"
      echo "ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)"
    } > "$LOG_FILE"
  else
    # Ensure header and update date
    if ! head -n 1 "$LOG_FILE" | grep -q '^feature_id:'; then
      TMPF="$TMP_DIR/creation_run.header.tmp"
      {
        echo "feature_id: $FEATURE_ID"
        echo "doc_type: governance.creation_run"
        echo "schema_ref: urn:automatr:schema:capsule:$FEATURE_ID:governance.creation_run:v1@0.1.0"
        echo "version: 0.1.0"
        echo "updated: $TODAY"
        echo
      } > "$TMPF"
      cat "$LOG_FILE" >> "$TMPF"
      mv "$TMPF" "$LOG_FILE"
    else
      sed -i -E "1,12 s/^updated: .*/updated: $TODAY/" "$LOG_FILE"
    fi
    # Ensure main table header present
    if ! grep -q '^Step \| Doc \| Gate \| Key decisions \| Links' "$LOG_FILE"; then
      printf "\nStep | Doc | Gate | Key decisions | Links\n--- | --- | --- | --- | ---\n" >> "$LOG_FILE"
    fi
    # Ensure UNKNOWN Summary present
    if ! grep -q '^## UNKNOWN Summary' "$LOG_FILE"; then
      printf "\n## UNKNOWN Summary\nID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)\n" >> "$LOG_FILE"
    fi
  fi
  # Auto-increment step if not provided
  if [[ -z "$STEP_LABEL" ]]; then
    LAST_STEP=$(grep -E '^[0-9]+ \|' "$LOG_FILE" | tail -n 1 | awk -F'|' '{print $1}' | tr -d ' ')
    if [[ -z "$LAST_STEP" ]]; then STEP_LABEL=1; else STEP_LABEL=$(( LAST_STEP + 1 )); fi
  fi
  DOC_DISPLAY="${DOC_PATH:-(all)}"
  echo "$STEP_LABEL | $DOC_DISPLAY | $GATE | ${DECISIONS:--} | ${LINKS:--}" >> "$LOG_FILE"

  # Append UNKNOWNs into run log (dedup)
  if [[ -s "$UNK_OUT" ]]; then
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      [[ "$line" == File:* ]] && continue
      [[ "$line" == ID\ \|* ]] && continue
      if ! grep -Fq "$line" "$LOG_FILE"; then
        echo "$line" >> "$LOG_FILE"
      fi
    done < "$UNK_OUT"
  fi

  # Also emit a brief validation summary
  SUM_FILE="$REPORT_DIR/validation_summary.md"
  {
    echo "## Validation Run"
    echo "Gate: $GATE"
    echo "Warnings: $WARN_COUNT, Failures: $FAIL_COUNT"
    echo "\n### Registry\n"; cat "$REG_OUT" || true
    echo "\n### Headers\n"; cat "$HDR_OUT" || true
    echo "\n### Acceptance/Schema\n"; cat "$ACC_OUT" || true
    echo "\n### Concurrency\n"; cat "$CON_OUT" || true
    echo "\n### Leak/Size\n"; cat "$LEAK_OUT" || true
    echo "\n### Unknowns\n"; cat "$UNK_OUT" || true
    echo "\n### Unknowns Policy\n"; cat "$UNKB_OUT" || true
    echo "\n### Implementable Check\n"; cat "$IMPL_OUT" || true
    echo "\n### Creation Run Check\n"; cat "$CRUN_OUT" || true
  } > "$SUM_FILE"
fi

echo "== Summary =="
echo "GATE: $GATE (warnings=$WARN_COUNT, failures=$FAIL_COUNT)"
if [[ "${REQUIRE_IMPLEMENTABLE:-0}" == "1" && "$GATE" == "WARN" ]]; then
  echo "Escalating WARN to FAIL due to REQUIRE_IMPLEMENTABLE=1"
  GATE="FAIL"; ((FAIL_COUNT++)); [[ -z "$STOP_REASON" ]] && STOP_REASON="WARN present under implementable enforcement"
fi
if [[ "$GATE" == "FAIL" ]]; then
  echo "STOP: $STOP_REASON"
  # Provide a heuristic NEED suggestion
  if [[ "$STOP_REASON" == *"Header validation"* ]]; then
    echo "NEED: Fix header order/fields and canonical schema_ref URN"
  elif [[ "$STOP_REASON" == *"Registry"* ]]; then
    echo "NEED: Ensure prompts/registry.json matches templates, then rerun"
  elif [[ "$STOP_REASON" == *"Prompt leakage"* ]]; then
    echo "NEED: Remove meta-prompt text from generated docs"
  elif [[ "$STOP_REASON" == *"size threshold"* ]]; then
    echo "NEED: Reduce document length or set VALIDATION_ALLOW_HARD_SIZE=1 with approval"
  elif [[ "$STOP_REASON" == *"Concurrency"* ]]; then
    echo "NEED: Add Concurrency Targets/Budget and concurrency_targets to schema"
  elif [[ "$STOP_REASON" == *"Implementable"* ]]; then
     echo "NEED: Ensure all required docs exist and headers are valid; resolve blocking UNKNOWNs"
  fi
else
  # If implementable enforcement is on and all checks passed, mark IMPLEMENTABLE
  if [[ -n "$FEATURE_ID" && -d "$ROOT_DIR/features/$FEATURE_ID" && "${REQUIRE_IMPLEMENTABLE:-0}" == "1" ]]; then
    LOG_FILE="$ROOT_DIR/features/$FEATURE_ID/reports/creation_run.md"
    TODAY=$(date +%F)
    if [[ -f "$LOG_FILE" ]]; then
      if ! grep -q '^## IMPLEMENTABLE' "$LOG_FILE"; then
        printf "\n## IMPLEMENTABLE\nStatus: Ready for code-generation\nDate: %s\n" "$TODAY" >> "$LOG_FILE"
      fi
    fi
    CLOG="$ROOT_DIR/features/$FEATURE_ID/CHANGELOG.md"
    if [[ -f "$CLOG" ]]; then
      echo "$TODAY | 0.1.0 | governance.creation_run: Marked IMPLEMENTABLE" >> "$CLOG"
    fi
  fi
fi

echo "== Done =="

exit $([[ "$GATE" == "FAIL" ]] && echo 1 || echo 0)
