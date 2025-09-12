#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]

def extract_unknown_rows(md_path: Path):
    try:
        text = md_path.read_text(encoding='utf-8')
    except Exception:
        return []
    # Capture the UNKNOWN Summary section content until the next heading or EOF
    pat = re.compile(r"^## UNKNOWN Summary\n(?P<table>(?:.*\n)+?)^(?:## |\Z)", re.M)
    m = pat.search(text)
    if not m:
        return []
    rows = [r.strip() for r in m.group('table').splitlines() if '|' in r]
    # Drop header line if present
    rows = [r for r in rows if not r.lower().startswith('id |') and r]
    return rows

def main():
    for base in (ROOT / 'features', ROOT / 'capsule'):
        if not base.exists():
            continue
        for p in base.rglob('*.md'):
            # Skip program reports under capsule/reports
            if p.as_posix().startswith((ROOT / 'capsule' / 'reports').as_posix()):
                continue
            rows = extract_unknown_rows(p)
            if rows:
                print(f"File: {p}")
                print("ID | Question | Possible Effects | Recommended Actions | Next Step | Impact (High/Moderate/Low)")
                for r in rows:
                    print(r)
                print()

if __name__ == '__main__':
    main()
