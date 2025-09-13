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

# BEGIN capsule-helpers make
.PHONY: sync-feature pack-demo watch-validate e2e-feature e2e-auto

# Sync capsule docs into features/<id> for packaging
# Usage: make sync-feature FID=<feature-id>
sync-feature:
	@if [ -z "$(FID)" ]; then echo "Usage: make sync-feature FID=<feature-id>" >&2; exit 2; fi; \
	set -e; \
	CAP="capsule/$(FID)"; FEAT="features/$(FID)"; \
	[ -d "$$CAP" ] || { echo "Missing $$CAP" >&2; exit 3; }; \
	mkdir -p "$$FEAT"; \
	for f in $$(ls "$$CAP"/*.md 2>/dev/null || true); do cp -f "$$f" "$$FEAT/"; done; \
	[ -f "$$CAP/output_contract.schema.json" ] && cp -f "$$CAP/output_contract.schema.json" "$$FEAT/" || true; \
	[ -f "$$FEAT/CHANGELOG.md" ] || printf "Init\n" > "$$FEAT/CHANGELOG.md"; \
	echo "Synced $$CAP -> $$FEAT"

# Create mock OS packaging artifacts from the latest bundle (tarballs as placeholders)
pack-demo:
	@set -e; \
	B=$$(ls -1d final_feature_documents/* 2>/dev/null | tail -n 1); \
	if [ -z "$$B" ]; then echo "No bundles found under final_feature_documents/" >&2; exit 4; fi; \
	mkdir -p planning/build-tests; \
	tar czf planning/build-tests/demo-linux.tgz -C "$$B" .; \
	cp -f planning/build-tests/demo-linux.tgz planning/build-tests/demo-macos.tgz; \
	cp -f planning/build-tests/demo-linux.tgz planning/build-tests/demo-windows.tgz; \
	echo "Pack-demo artifacts in planning/build-tests/"

# Simple polling watcher that validates on changes (Ctrl+C to stop)
watch-validate:
	@TS=$$(date +%s); \
	mkdir -p planning/reports; \
	while sleep 2; do \
	  N=$$(find capsule tools/capsule-engine -type f -newermt "@$$TS" | wc -l); \
	  if [ "$$N" -gt 0 ]; then \
	    TS=$$(date +%s); \
	    FEATURE_ID="$(FID)" bash capsule/reports/validation/validate_all.sh >> planning/reports/auto_watch.log 2>&1 || true; \
	    date -Is >> planning/reports/auto_watch.log; \
	    echo "Validated (FID=$$(echo $(FID)))" >> planning/reports/auto_watch.log; \
	    echo "Validation run appended to planning/reports/auto_watch.log"; \
	  fi; \
	done

# End-to-end flow with LLM-guided steps
# Usage: make e2e-feature FID=<feature-id> [ALLOW=yes|no]
e2e-feature:
	@if [ -z "$(FID)" ]; then echo "Usage: make e2e-feature FID=<feature-id> [ALLOW=yes|no]" >&2; exit 2; fi; \
	printf "\nLLM> We will create feature '%s'.\n" "$(FID)"; \
	printf "LLM> The wizard will ask for the Feature ID. Please enter: %s\n\n" "$(FID)"; \
	python3 tools/capsule-engine/entrypoint.py wizard; \
	printf "\n"; \
	read -r -p "LLM> Sync docs into features/$(FID) for packaging? [Y/n] " ans; ans=$${ans:-Y}; \
	case $$ans in [Yy]*) $(MAKE) sync-feature FID=$(FID);; esac; \
	printf "\n"; \
	read -r -p "LLM> Run validation with implementable gate? [Y/n] " ans2; ans2=$${ans2:-Y}; \
	case $$ans2 in [Yy]*) python3 tools/capsule-engine/entrypoint.py validate --feature-id $(FID) --require-implementable ;; esac; \
	printf "\n"; \
	read -r -p "LLM> Package now? [y/N] " ans3; ans3=$${ans3:-N}; \
	if echo $$ans3 | grep -qi '^y'; then \
	  read -r -p "LLM> Allow >1600 tokens in brief? [y/N] " ans4; ans4=$${ans4:-N}; \
	  allow=$$(echo $$ans4 | grep -qi '^y' && echo yes || echo no); \
	  bash tools/capsule-engine/tools/final_bundle/verify_and_package.sh feature_id=$(FID) allow_gt_1600_tokens=$$allow; \
	  read -r -p "LLM> Create mock OS tarballs from latest bundle? [y/N] " ans5; ans5=$${ans5:-N}; \
	  case $$ans5 in [Yy]*) $(MAKE) pack-demo;; esac; \
	fi; \
	echo "\nLLM> e2e complete for $(FID)."

# End-to-end auto flow (non-interactive) with optional seed file
# Usage: make e2e-auto FID=<feature-id> [SEED=path] [ALLOW=yes|no]
e2e-auto:
	@if [ -z "$(FID)" ]; then echo "Usage: make e2e-auto FID=<feature-id> [SEED=path] [ALLOW=yes|no]" >&2; exit 2; fi; \
	python3 tools/capsule-engine/entrypoint.py auto --feature-id "$(FID)" $$( [ -n "$(FROM)" ] && printf -- " --from-template %s" "$(FROM)" ) $$( [ -n "$(SEED)" ] && printf -- " --seed %s" "$(SEED)" ) $$( [ "$(ALLOW)" = "yes" ] && printf -- " --allow-gt-1600 yes" || printf -- " --allow-gt-1600 no" ) $$( [ "$(FORCE)" = "yes" ] && printf -- " --force" )
# END capsule-helpers make
