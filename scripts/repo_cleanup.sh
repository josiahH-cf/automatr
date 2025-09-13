#!/usr/bin/env bash
set -euo pipefail

# Repository cleanup helper with dry-run and confirmation.
# Lists and removes items not required for the capsule workflow.
#
# Usage:
#   scripts/repo_cleanup.sh            # dry-run (default)
#   scripts/repo_cleanup.sh --confirm  # perform deletions after prompt

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

confirm=0
if [[ "${1:-}" == "--confirm" ]]; then
  confirm=1
fi

keep=(
  ".git"
  ".gitattributes"
  ".gitignore"
  "LICENSE"
  "README.md"
  "capsule.project.toml"
  "Makefile"
  "scripts"
  "scripts/one_time_engine_audit.sh"
  "docs"
  "docs/final_bundle_usage.md"
  "automatr-capsule"
  "capsule"
  "features"
  "planning"
  "final_feature_documents"
  "tools"
  "tools/capsule-engine"
  "tools/capsule-engine/tools/final_bundle"
  ".github"
  ".github/context.md"
)

is_kept() {
  local path="$1"
  for k in "${keep[@]}"; do
    if [[ "$path" == "$k" || "$path" == $k/* ]]; then
      return 0
    fi
  done
  return 1
}

echo "== Cleanup (dry-run by default) =="
echo "Root: $ROOT_DIR"

mapfile -t entries < <(ls -A)
to_delete=()
for e in "${entries[@]}"; do
  if is_kept "$e"; then
    continue
  fi
  to_delete+=("$e")
done

if (( ${#to_delete[@]} == 0 )); then
  echo "Nothing to delete. Repo already clean."
  exit 0
fi

echo "Candidates for deletion:" 
for e in "${to_delete[@]}"; do
  echo " - $e"
done

if (( confirm == 0 )); then
  echo "\nDRY-RUN: no files were deleted. Re-run with --confirm to proceed."
  exit 0
fi

read -r -p "Proceed to delete these items? [y/N] " ans
ans=${ans:-N}
if [[ ! "$ans" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

for e in "${to_delete[@]}"; do
  if [[ -e "$e" || -L "$e" ]]; then
    rm -rf -- "$e"
  fi
done

echo "Done."

