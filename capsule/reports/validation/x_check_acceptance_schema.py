#!/usr/bin/env python3
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def check_pair(base: Path):
    intent = base / 'intent_card.md'
    schema = base / 'output_contract.schema.json'
    if not intent.exists() or not schema.exists():
        return []
    try:
        data = json.loads(schema.read_text(encoding='utf-8'))
    except Exception as e:
        return [(str(schema), f'ERROR reading schema: {e}')]
    required = data.get('required') or []
    if not required:
        return [(str(schema), 'INFO: output_contract required[] empty; skipping mapping check')]
    # Extract mapping lines from intent_card.md under the mapping table header if present
    lines = intent.read_text(encoding='utf-8').splitlines()
    mapping_rows = []
    in_map = False
    for ln in lines:
        if ln.strip().lower().startswith('checklist') and 'schema' in ln.lower():
            in_map = True
            continue
        if in_map:
            if not ln.strip():
                break
            if '|' in ln:
                mapping_rows.append([c.strip() for c in ln.split('|') if c.strip()])
            else:
                break
    mapped = set()
    for row in mapping_rows:
        for cell in row:
            if cell.startswith('required ') or cell == 'Required Field':
                continue
        if len(row) >= 2:
            mapped.add(row[1])
    missing = [k for k in required if k not in mapped]
    if missing:
        return [(str(intent), f"WARN: acceptance→schema mapping missing keys: {missing}")]
    return [(str(intent), 'OK: acceptance→schema mapping covers required keys')]

def main():
    messages = []
    for root in (ROOT / 'capsule', ROOT / 'features'):
        if not root.exists():
            continue
        for p in root.glob('*'):
            if not p.is_dir():
                continue
            messages.extend(check_pair(p))
    for path, msg in messages:
        print(f"{path}: {msg}")

if __name__ == '__main__':
    main()

