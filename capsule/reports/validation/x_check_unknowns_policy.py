#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def extract_unknown_rows(md_path: Path):
    try:
        text = md_path.read_text(encoding='utf-8')
    except Exception:
        return []
    pat = re.compile(r"^## UNKNOWN Summary\n(?P<table>(?:.*\n)+?)^(?:## |\Z)", re.M)
    m = pat.search(text)
    if not m:
        return []
    rows = [r.strip() for r in m.group('table').splitlines() if '|' in r]
    rows = [r for r in rows if not r.lower().startswith('id |') and r]
    return rows

def check_unknowns(base: Path):
    msgs = []
    for p in base.rglob('*.md'):
        if p.as_posix().startswith((ROOT / 'capsule' / 'reports').as_posix()):
            continue
        rows = extract_unknown_rows(p)
        for r in rows:
            # Expect 6 columns
            parts = [c.strip() for c in r.split('|') if c.strip()]
            if len(parts) < 6:
                msgs.append((str(p), f"FAIL: UNKNOWN row malformed: {r}"))
                continue
            impact = parts[-1]
            if impact.lower().startswith('high'):
                msgs.append((str(p), "FAIL: UNKNOWN with High impact present"))
    return msgs

def main():
    for base in (ROOT / 'features',):
        if not base.exists():
            continue
        for fid_dir in base.glob('*'):
            if not fid_dir.is_dir():
                continue
            for path, msg in check_unknowns(fid_dir):
                print(f"{path}: {msg}")

if __name__ == '__main__':
    main()

