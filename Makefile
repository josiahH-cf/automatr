# BEGIN portable-engine make
.PHONY: plan-validate plan-package plan-info

# Validate a doc or full tree (variables pass through)
# Examples:
#   make plan-validate FID=my-feature
#   make plan-validate FID=my-feature DOC=features/my-feature/vision.md STEP=1
plan-validate:
	@FEATURE_ID="$(FID)" DOC_PATH="$(DOC)" STEP="$(STEP)" \
	bash tools/capsule-engine/capsule/reports/validation/validate_all.sh

# Package a feature capsule (variables pass through)
# Example:
#   make plan-package FID=my-feature ALLOW=no
plan-package:
	@tools/capsule-engine/tools/final_bundle/verify_and_package.sh \
	feature_id="$(FID)" allow_gt_1600_tokens="$(ALLOW)"

# Discovery helper
plan-info:
	@echo "Engine dir: tools/capsule-engine"
	@echo "Planning dir: automatr-capsule/planning"
# END portable-engine make

# BEGIN capsule-workflow make
.PHONY: new-feature engine-check-generic

# Create a new feature via interactive wizard by default
# Usage: make new-feature [FID=my-feature FROM=... DRY=yes FORCE=yes] (non-interactive when FID is provided)
new-feature:
	@if [ -n "$(FID)" ]; then \
	  echo "Non-interactive: creating new feature '$(FID)'"; \
	  python3 tools/capsule-engine/entrypoint.py new --feature-id "$(FID)" $$( [ -n "$(FROM)" ] && printf -- " --from-template %s" "$(FROM)" ) $$( [ "$(DRY)" = "yes" ] && printf -- " --dry-run" ) $$( [ "$(FORCE)" = "yes" ] && printf -- " --force" ); \
	else \
	  python3 tools/capsule-engine/entrypoint.py wizard; \
	fi

# One-time audit to ensure engine is generic and clean
engine-check-generic:
	@python3 tools/capsule-engine/scripts/check_generic.py || true
	@bash scripts/one_time_engine_audit.sh

# END capsule-workflow make
