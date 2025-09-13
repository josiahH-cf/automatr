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

# Remove placeholder template directories inside app capsule/features
placeholder_candidates=()
while IFS= read -r -d '' d; do
  placeholder_candidates+=("$d")
done < <(find automatr-capsule -type d \( -name '<feature_id>' -o -name '{{FEATURE_ID}}' \) -print0 2>/dev/null || true)

if (( ${#placeholder_candidates[@]} > 0 )); then
  echo "Found placeholder directories (will remove on confirm):"
  for d in "${placeholder_candidates[@]}"; do
    echo " - $d"
  done
  to_delete+=("${placeholder_candidates[@]}")
fi

# Remove validation temp artifacts if present
val_tmp="tools/capsule-engine/capsule/reports/validation/.run_tmp"
if [[ -d "$val_tmp" ]]; then
  echo "Found validation temp dir: $val_tmp (will remove on confirm)"
  to_delete+=("$val_tmp")
fi

# Remove redundant planning mirrors (top-level symlinks already expose these)
for p in automatr-capsule/planning/features automatr-capsule/planning/final_feature_documents; do
  if [[ -d "$p" ]]; then
    echo "Found redundant planning mirror: $p (will remove on confirm)"
    to_delete+=("$p")
  fi
done

dup_packager=()
if [[ -f tools/capsule-engine/tools/verify_and_package.sh ]]; then dup_packager+=("tools/capsule-engine/tools/verify_and_package.sh"); fi
if [[ -f tools/capsule-engine/tools/verify_and_package.py ]]; then dup_packager+=("tools/capsule-engine/tools/verify_and_package.py"); fi
if (( ${#dup_packager[@]} > 0 )); then
  echo "WARNING: duplicate packager scripts detected outside final_bundle (submodule)." >&2
  for f in "${dup_packager[@]}"; do echo " - $f" >&2; done
fi

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
