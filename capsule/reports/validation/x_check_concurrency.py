#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]

def has_md_concurrency(path: Path, titles: list[str]) -> tuple[bool, str]:
    try:
        txt = path.read_text(encoding='utf-8')
    except Exception:
        return False, "unreadable"
    low = txt.lower()
    title_ok = any(f"## {t.lower()}" in low for t in titles)
    if not title_ok:
        return False, "missing section"
    # check indicative column labels
    hints = [
        ("throughput", "rps"),
        ("latency", "ms"),
        ("error budget", "%"),
        ("window", "day"),
    ]
    found = 0
    for a, b in hints:
        if a in low and b in low:
            found += 1
    return (found >= 3), ("columns ok" if found >= 3 else "columns incomplete")

def has_schema_concurrency(path: Path) -> tuple[bool, str]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        return False, f"schema unreadable: {e}"
    ct = data.get('concurrency_targets')
    if not isinstance(ct, dict):
        return False, "concurrency_targets missing"
    required_keys = ['throughput_rps', 'latency_ms', 'error_budget_pct', 'window_days']
    missing = [k for k in required_keys if k not in ct]
    if missing:
        return False, f"missing keys: {missing}"
    lat = ct.get('latency_ms')
    if not isinstance(lat, dict) or not all(k in lat for k in ('p50','p95','p99')):
        return False, "latency_ms missing p50/p95/p99"
    return True, "ok"

def main():
    checks = []
    for base in (ROOT / 'capsule', ROOT / 'features'):
        if not base.exists():
            continue
        for p in base.glob('*'):
            if not p.is_dir():
                continue
            intent = p / 'intent_card.md'
            action = p / 'action_budget.md'
            outc = p / 'output_contract.schema.json'
            if intent.exists():
                ok, note = has_md_concurrency(intent, ['Concurrency Targets'])
                checks.append((intent, 'Concurrency tuple (md)', ok, note))
            if action.exists():
                ok, note = has_md_concurrency(action, ['Concurrency Budget', 'Concurrency Targets'])
                checks.append((action, 'Concurrency tuple (md)', ok, note))
            if outc.exists():
                ok, note = has_schema_concurrency(outc)
                checks.append((outc, 'Concurrency tuple (schema)', ok, note))
    for path, what, ok, note in checks:
        state = 'OK' if ok else 'WARN'
        print(f"{path}: {state}: {what} - {note}")

if __name__ == '__main__':
    main()
