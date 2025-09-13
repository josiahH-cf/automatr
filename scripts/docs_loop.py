#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

ORDER = [
    "intent_card.md",
    "output_contract.schema.json",
    "vision.md",
    "exploration.md",
    "assumptions.md",
    "reference_set.md",
    "observability_slos.md",
    "concurrency_model.md",
    "action_budget.md",
    "sync_policies.md",
    "test_plan.md",
    "manual_tests.md",
    "runtime_concurrency_tests.md",
    "validation_report.md",
    "phase_transition.md",
    "audit_log.md",
]

def app_root() -> Path:
    return Path(__file__).resolve().parents[1]

def validate(fid: str, require_impl: bool = True) -> int:
    cmd = [
        sys.executable,
        str(app_root() / "tools/capsule-engine/entrypoint.py"),
        "validate",
        "--feature-id",
        fid,
    ]
    if require_impl:
        cmd.append("--require-implementable")
    print("\n== Running validation ==")
    return subprocess.call(cmd)

def package(fid: str, allow: str = "no") -> int:
    # Use engine entrypoint for packaging to avoid hardcoded script paths
    cmd = [
        sys.executable,
        str(app_root() / "tools/capsule-engine/entrypoint.py"),
        "package",
        "--feature-id",
        fid,
        "--allow-gt-1600",
        allow,
    ]
    print("\n== Packaging ==")
    return subprocess.call(cmd)

def print_batch_prompt(fid: str, files):
    print("\n===== Authoring Batch =====")
    print("Feature:", fid)
    print("Edit these under features/%s/:" % fid)
    for f in files:
        print(" - features/%s/%s" % (fid, f))
    print("\nReminder: Keep headers; maintain mapping↔schema; ensure concurrency tuple appears in intent_card + action_budget + schema.")
    print("Press Enter to validate this batch...")

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Iterate docs in batches with validation")
    p.add_argument("--feature-id", required=True)
    p.add_argument("--batch-size", type=int, default=6)
    p.add_argument("--pack", default="no", choices=["yes", "no"])
    p.add_argument("--allow-gt-1600", default="no", choices=["yes", "no"])
    args = p.parse_args(argv)

    fid = args.feature_id
    batch = args.batch_size

    first = ["intent_card.md", "output_contract.schema.json"]
    print_batch_prompt(fid, first)
    input()
    if validate(fid, True) != 0:
        print("Validation failed; fix and press Enter to re-run...")
        input();
        if validate(fid, True) != 0:
            return 1

    rest = [f for f in ORDER if f not in first]
    for i in range(0, len(rest), batch):
        chunk = rest[i:i+batch]
        print_batch_prompt(fid, chunk)
        input()
        if validate(fid, True) != 0:
            print("Validation failed; fix and press Enter to re-run...")
            input();
            if validate(fid, True) != 0:
                return 1

    if args.pack == "yes":
        return package(fid, args.allow_gt_1600)
    print("\nAll batches validated. Package when ready:")
    print(
        f"python3 tools/capsule-engine/entrypoint.py package --feature-id {fid} --allow-gt-1600 {args.allow_gt_1600}"
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())

