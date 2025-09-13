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

# Create a new feature from the engine template
# Usage: make new-feature FID=my-feature [DRY=yes] [FORCE=yes]
new-feature:
	@FEATURE_ID="$(FID)" DRY_RUN="$(DRY)" FORCE="$(FORCE)" bash tools/capsule-engine/scripts/new_feature.sh $$FEATURE_ID $$( [ -n "$(FROM)" ] && printf -- " --from-template %s" "$(FROM)" ) $$( [ -n "$(DRY)" ] && printf -- " --dry-run %s" "$(DRY)" ) $$( [ "$(FORCE)" = "yes" ] && printf -- " --force" )

# One-time audit to ensure engine is generic and clean
engine-check-generic:
	@bash scripts/one_time_engine_audit.sh

# END capsule-workflow make
