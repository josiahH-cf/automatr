#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
VALIDATION_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "== Checking prompts registry =="
if command -v python3 >/dev/null 2>&1; then
  python3 "$VALIDATION_DIR/check_registry.py"
elif command -v python >/dev/null 2>&1; then
  python "$VALIDATION_DIR/check_registry.py"
else
  echo "WARNING: Python not found; skipping registry check" >&2
fi

echo "== Validating generated documents (with doc_type) =="
FOUND=0
while IFS= read -r -d '' file; do
  if grep -q '^doc_type:' "$file"; then
    # Skip placeholder skeletons that use the literal '<feature-id>'
    fid=$(awk -F': ' '/^feature_id:/ {print $2; exit}' "$file")
    if [[ "$fid" == "<feature-id>" || -z "$fid" ]]; then
      echo "SKIP skeleton: $file"
      continue
    fi
    FOUND=1
    if command -v python3 >/dev/null 2>&1; then
      python3 "$VALIDATION_DIR/check_document_headers.py" "$file"
    else
      python "$VALIDATION_DIR/check_document_headers.py" "$file" || true
    fi
  fi
done < <(find "$ROOT_DIR/capsule" -type f -name "*.md" -print0 2>/dev/null)

if [[ "$FOUND" -eq 0 ]]; then
  echo "Note: No generated documents with 'doc_type:' found yet; header validation skipped."
fi

echo "== Done =="
