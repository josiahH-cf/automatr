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
	@echo "Planning dir: planning"
# END portable-engine make
