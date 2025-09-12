#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]

GATE_VALUES = {"PASS", "WARN", "FAIL"}


def check_log(path: Path):
    msgs = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [(str(path), f"FAIL: unreadable: {e}")]

    # Check header presence
    if not text.startswith("feature_id:") or "\ndoc_type: governance.creation_run\n" not in text:
        msgs.append((str(path), "FAIL: missing or invalid header"))

    # Table header
    if "Step | Doc | Gate | Key decisions | Links" not in text:
        msgs.append((str(path), "FAIL: main table header missing"))

    # Check steps order and gate values
    steps = []
    for line in text.splitlines():
        if re.match(r"^\d+\s*\|", line):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                try:
                    step = int(parts[0])
                    gate = parts[2]
                except ValueError:
                    continue
                steps.append((step, gate))
    if steps:
        # Strictly increasing by 1
        prev = None
        for step, gate in steps:
            if prev is None:
                prev = step
            else:
                if step != prev + 1:
                    msgs.append((str(path), f"FAIL: out-of-order or missing step around {prev}->{step}"))
                    break
                prev = step
            if gate not in GATE_VALUES:
                msgs.append((str(path), f"FAIL: invalid Gate value '{gate}' in step {step}"))
    else:
        msgs.append((str(path), "WARN: no steps recorded yet"))

    # UNKNOWN Summary presence
    if "## UNKNOWN Summary" not in text:
        msgs.append((str(path), "WARN: UNKNOWN Summary section missing"))

    return msgs


def main():
    for base in (ROOT / 'features',):
        if not base.exists():
            continue
        for p in base.glob('*/reports/creation_run.md'):
            for path, msg in check_log(p):
                print(f"{path}: {msg}")


if __name__ == '__main__':
    main()

