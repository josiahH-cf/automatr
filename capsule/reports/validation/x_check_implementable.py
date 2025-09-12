#!/usr/bin/env python3
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[3]

REQUIRED_FILES = [
    'vision.md',
    'exploration.md',
    'intent_card.md',
    'output_contract.schema.json',
    'action_budget.md',
    'concurrency_model.md',
    'sync_policies.md',
    'reference_set.md',
    'assumptions.md',
    'evaluation_and_tripwires.md',
    'meta_prompts.md',
    'test_plan.md',
    'runtime_concurrency_tests.md',
    'observability_slos.md',
    'manual_tests.md',
    'validation_report.md',
    'audit_log.md',
    'phase_transition.md',
    'CHANGELOG.md',
    'reports/creation_run.md',
    'reports/manual_tests.md',
    'reports/chaos_results.md',
]

HEADER_REQUIRED = ["feature_id", "doc_type", "schema_ref", "version", "updated"]


def parse_header(text: str):
    header = {}
    for line in text.splitlines():
        if not line.strip():
            if header:
                break
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            header[k.strip()] = v.strip()
        if len(header) >= 5:
            pass
    return header


def check_headers(base: Path):
    msgs = []
    for p in base.rglob('*.md'):
        try:
            text = p.read_text(encoding='utf-8')
        except Exception as e:
            msgs.append((str(p), f'FAIL: unreadable: {e}'))
            continue
        if 'doc_type:' not in text.splitlines()[:50]:
            continue
        header = parse_header(text)
        missing = [k for k in HEADER_REQUIRED if k not in header]
        if missing:
            msgs.append((str(p), f'FAIL: missing header fields: {missing}'))
        sref = header.get('schema_ref', '')
        if not re.match(r'^urn:automatr:schema:capsule:[a-z0-9-]+:[a-z0-9_.-]+:v\d+@[^\s]+$', sref):
            msgs.append((str(p), 'FAIL: invalid schema_ref format'))
    return msgs


def main():
    fid = os.environ.get('FEATURE_ID')
    if not fid:
        print('INFO: FEATURE_ID not set; implementable check skipped')
        return
    base = ROOT / 'features' / fid
    if not base.exists():
        print(f'FAIL: feature folder missing: {base}')
        return

    missing = [rel for rel in REQUIRED_FILES if not (base / rel).exists()]
    if missing:
        print(f'{base}: FAIL: missing required documents: {missing}')
    else:
        print(f'{base}: OK: all required documents present')

    for path, msg in check_headers(base):
        print(f'{path}: {msg}')


if __name__ == '__main__':
    main()

