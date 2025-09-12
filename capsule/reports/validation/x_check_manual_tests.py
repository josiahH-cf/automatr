#!/usr/bin/env python3
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

TESTS_HEADER_RE = re.compile(r"^\s*ID\s*\|\s*Test Name\s*\|\s*Inputs\s*\|\s*Expected Result\s*\|\s*Linked Schema Key\s*\|\s*Status\s*$", re.I)


def parse_tests_table(text: str):
    # Find the Tests section and parse the main table
    lines = text.splitlines()
    in_tests = False
    header_idx = None
    rows = []
    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("## tests"):
            in_tests = True
            continue
        if in_tests:
            if ln.strip().startswith("## "):
                break
            if header_idx is None and TESTS_HEADER_RE.match(ln.strip()):
                header_idx = i
                continue
            if header_idx is not None and '|' in ln and ln.strip() and not ln.strip().startswith('|-'):
                parts = [p.strip() for p in ln.split('|')]
                # Expect 6 columns; be tolerant to leading/ending pipes
                parts = [p for p in parts if p != '']
                if len(parts) >= 6:
                    rows.append(parts[:6])
    return rows


def extract_contract_ref(text: str):
    # Look for a Contract reference line in Schema Reference section
    m = re.search(r"^\s*Contract:\s*(urn:automatr:[^\s]+)$", text, re.M)
    return m.group(1) if m else None


def check_feature(base: Path):
    msgs = []
    schema_path = base / 'output_contract.schema.json'
    tests_path = base / 'manual_tests.md'
    intent_path = base / 'intent_card.md'

    if not schema_path.exists():
        return msgs
    try:
        schema = json.loads(schema_path.read_text(encoding='utf-8'))
    except Exception as e:
        msgs.append((str(schema_path), f'FAIL: schema unreadable: {e}'))
        return msgs

    required = schema.get('required') or []
    schema_ver = schema.get('version', '')

    if not tests_path.exists():
        if required:
            msgs.append((str(tests_path), 'FAIL: manual_tests.md missing while schema.required is non-empty'))
        else:
            msgs.append((str(tests_path), 'WARN: manual_tests.md missing but schema.required is empty'))
        return msgs

    text = tests_path.read_text(encoding='utf-8')
    # Contract version alignment
    contract_ref = extract_contract_ref(text)
    if contract_ref and '@' in contract_ref:
        ver_ref = contract_ref.rsplit('@', 1)[-1]
        if ver_ref != schema_ver:
            msgs.append((str(tests_path), f'FAIL: schema version mismatch (tests {ver_ref} vs schema {schema_ver})'))
    else:
        # Encourage explicit schema reference
        msgs.append((str(tests_path), 'WARN: Schema Reference missing or unversioned'))

    # Parse Tests table
    rows = parse_tests_table(text)
    if required and not rows:
        msgs.append((str(tests_path), 'FAIL: Tests table missing while schema.required is non-empty'))
        return msgs

    # Determine Linked Schema Key column index (5th in our structure)
    linked_keys = [r[4] for r in rows if len(r) >= 5]
    covered = set([k.strip('` ') for k in linked_keys if k.strip()])
    missing = [k for k in required if k not in covered]
    if missing:
        msgs.append((str(tests_path), f'FAIL: required keys without tests: {missing}'))
    else:
        if required:
            msgs.append((str(tests_path), 'OK: all required schema keys covered by tests'))

    # Basic acceptance mapping presence (optional guidance)
    if '## Acceptance-to-Test Mapping' not in text:
        msgs.append((str(tests_path), 'WARN: Acceptance-to-Test Mapping section missing'))

    # Encourage presence of a reports file
    reports_md = base / 'reports' / 'manual_tests.md'
    if not reports_md.exists():
        msgs.append((str(reports_md), 'WARN: test run log not found; create /reports/manual_tests.md'))
    return msgs


def main():
    for root in (ROOT / 'features', ROOT / 'capsule'):
        if not root.exists():
            continue
        for p in root.glob('*'):
            if not p.is_dir():
                continue
            for path, msg in check_feature(p):
                print(f"{path}: {msg}")


if __name__ == '__main__':
    main()

