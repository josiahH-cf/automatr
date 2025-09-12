#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VALIDATION_DIR = Path(__file__).resolve().parent

FORBIDDEN = [
    re.compile(r"\bYou are an? (autonomous|AI|model)\b", re.I),
    re.compile(r"^Purpose\b", re.I),
    re.compile(r"^Template\b", re.I),
    re.compile(r"You are generating scaffolding documents only", re.I),
]

def load_extra_forbidden():
    extra_file = VALIDATION_DIR / 'forbidden_patterns.txt'
    if not extra_file.exists():
        return []
    pats = []
    for line in extra_file.read_text(encoding='utf-8').splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        try:
            pats.append(re.compile(s, re.I))
        except re.error:
            continue
    return pats

def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))

def check_file(path: Path):
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return []
    msgs = []
    for pat in FORBIDDEN:
        if pat.search(text):
            msgs.append((str(path), 'FAIL: possible prompt leakage'))
            break
    wc = word_count(text)
    # Rough token estimate ~0.75*words; alert near 800 tokens (~1067 words)
    if wc > 1600*1.35:
        msgs.append((str(path), f'HARD: size very large (~{wc} words)'))
    elif wc > 800*1.35:
        msgs.append((str(path), f'SOFT: size large (~{wc} words)'))
    return msgs

def main():
    results = []
    # Extend forbidden list dynamically
    FORBIDDEN.extend(load_extra_forbidden())
    for base in (ROOT / 'features', ROOT / 'capsule'):
        if not base.exists():
            continue
        for p in base.rglob('*.md'):
            # Skip program reports
            if '/reports/' in str(p.as_posix()) and 'features/' not in str(p.as_posix()):
                continue
            results.extend(check_file(p))
    for path, msg in results:
        print(f"{path}: {msg}")

if __name__ == '__main__':
    main()
