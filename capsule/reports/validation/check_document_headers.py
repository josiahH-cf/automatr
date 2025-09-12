#!/usr/bin/env python3
import re
import sys
from pathlib import Path

FEATURE_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:-v[0-9]+)?$")
SEMVER_RE = re.compile(r"^([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$")
UPDATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DOC_TYPE_RE = re.compile(r"^(planning|governance|quality)\.[a-z0-9_.-]+$")

def parse_header(path: Path, max_lines: int = 50):
    header = {}
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_lines:
                break
            line = line.rstrip("\n")
            if not line.strip():
                # stop at first blank line after collecting some fields
                if header:
                    break
                else:
                    continue
            if ":" in line:
                k, v = line.split(":", 1)
                header[k.strip()] = v.strip()
    return header

def main():
    if len(sys.argv) != 2:
        print("Usage: check_document_headers.py <document.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    header = parse_header(path)
    required = ["feature_id", "doc_type", "schema_ref", "version", "updated"]
    missing = [k for k in required if k not in header]
    issues = 0
    if missing:
        print(f"ERROR: missing header fields: {', '.join(missing)}", file=sys.stderr)
        issues += 1

    fid = header.get("feature_id", "")
    if fid and not FEATURE_ID_RE.match(fid):
        print(f"ERROR: invalid feature_id: {fid}", file=sys.stderr)
        issues += 1

    ver = header.get("version", "")
    if ver and not SEMVER_RE.match(ver):
        print(f"ERROR: invalid version (SemVer required): {ver}", file=sys.stderr)
        issues += 1

    upd = header.get("updated", "")
    if upd and not UPDATED_RE.match(upd):
        print(f"ERROR: invalid updated date (YYYY-MM-DD): {upd}", file=sys.stderr)
        issues += 1

    doc_type = header.get("doc_type", "")
    if doc_type and not DOC_TYPE_RE.match(doc_type):
        print(f"ERROR: invalid doc_type namespace: {doc_type}", file=sys.stderr)
        issues += 1

    schema_ref = header.get("schema_ref", "")
    # urn:automatr:schema:capsule:<feature_id>:<doc_type>:v<major>@<version>
    SCHEMA_RE = re.compile(r"^urn:automatr:schema:capsule:(?P<fid>[a-z0-9-]+):(?P<dtype>[a-z0-9_.-]+):v(?P<major>\d+)@(?P<ver>.+)$")
    m = SCHEMA_RE.match(schema_ref)
    if not m:
        print(f"ERROR: invalid schema_ref format: {schema_ref}", file=sys.stderr)
        issues += 1
    else:
        if fid and m.group("fid") != fid:
            print(f"ERROR: schema_ref feature_id mismatch: {m.group('fid')} != {fid}", file=sys.stderr)
            issues += 1
        if doc_type and m.group("dtype") != doc_type:
            print(f"ERROR: schema_ref doc_type mismatch: {m.group('dtype')} != {doc_type}", file=sys.stderr)
            issues += 1
        if ver and m.group("ver") != ver:
            print(f"ERROR: schema_ref version mismatch: {m.group('ver')} != {ver}", file=sys.stderr)
            issues += 1

    # Optional: enforce header order for the first required lines
    try:
        lines = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    lines.append(line.strip())
                if len(lines) == len(required):
                    break
        keys_in_order = [l.split(":", 1)[0].strip() for l in lines]
        expected_order = required
        if keys_in_order != expected_order:
            print(f"ERROR: header order invalid. Found {keys_in_order}, expected {expected_order}", file=sys.stderr)
            issues += 1
    except Exception:
        pass

    if issues == 0:
        print(f"OK: {path} header is valid")
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
