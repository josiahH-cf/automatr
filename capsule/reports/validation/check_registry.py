#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[3]  # .../automatr
REGISTRY = ROOT / "prompts" / "registry.json"
PROMPTS_DIR = ROOT / "prompts"

ALLOWED_PREFIX = re.compile(r"^(planning|governance|quality)\.[a-z0-9_.-]+$")

def eprint(*args):
    print(*args, file=sys.stderr)

def main():
    if not REGISTRY.exists():
        eprint(f"ERROR: registry not found at {REGISTRY}")
        return 2
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        eprint("ERROR: registry.json must be an object mapping doc_type -> prompt_path")
        return 2

    issues = 0

    # Check keys and referenced files
    values = set()
    for doc_type, rel_path in data.items():
        if not isinstance(doc_type, str) or not isinstance(rel_path, str):
            eprint(f"ERROR: invalid entry: {doc_type!r}: {rel_path!r}")
            issues += 1
            continue
        if not ALLOWED_PREFIX.match(doc_type):
            eprint(f"ERROR: invalid doc_type namespace: {doc_type}")
            issues += 1
        path = ROOT / rel_path
        values.add(str(Path(rel_path).as_posix()))
        if not path.exists():
            eprint(f"ERROR: missing template file for {doc_type}: {rel_path}")
            issues += 1

    # Check that all templates are registered
    present = set()
    for p in PROMPTS_DIR.glob("*_template.md"):
        present.add(str(p.relative_to(ROOT).as_posix()))

    unregistered = present - values
    if unregistered:
        for rel in sorted(unregistered):
            eprint(f"ERROR: template present but not in registry: {rel}")
        issues += len(unregistered)

    extra = values - present
    if extra:
        for rel in sorted(extra):
            eprint(f"ERROR: registry references non-template file: {rel}")
        issues += len(extra)

    if issues == 0:
        print("OK: registry and templates are consistent")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())

