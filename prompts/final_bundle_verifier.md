# Final Bundle Verifier (Operational Prompt)

You are running in a clean environment with no prior context.
Your task is to collect inputs and execute the local verifier/packager tool. Emit only the tool’s stdout/stderr.

Inputs to collect from the user:
- feature_id (kebab-case, required)
- allow_gt_1600_tokens (yes|no; default no)

Then run (prefer shell; fallback to Python):
- `tools/final_bundle/verify_and_package.sh feature_id=<feature_id> allow_gt_1600_tokens=<yes|no>`
- If shell is not available, run: `python3 tools/final_bundle/verify_and_package.py <feature_id> --allow-gt-1600-tokens <yes|no>`

Do not add extra commentary. Print exactly the script’s output.

