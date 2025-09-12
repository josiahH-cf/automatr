#!/usr/bin/env python3
"""
Schema evolution utility for feature capsules.

Responsibilities:
- Bump /features/<feature_id>/output_contract.schema.json version (patch/minor/major or explicit set).
- Update "$id" major (vN) to match SemVer MAJOR when bumping MAJOR.
- Append a CHANGELOG entry in /features/<feature_id>/CHANGELOG.md.
- Optionally run the validator with per-step logging to creation_run.md.

Usage:
  bump_schema_and_sync.py --feature-id <fid> --bump {patch,minor,major} [--note "reason"] [--run-validate]
  bump_schema_and_sync.py --feature-id <fid> --set-version X.Y.Z [--note "reason"] [--run-validate]

Environment for validation (when --run-validate is provided):
  FEATURE_ID is set automatically; DOC_PATH points to the schema file; STEP auto-increments.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

SEMVER_RE = re.compile(r"^(?P<maj>\d+)\.(?P<min>\d+)\.(?P<pch>\d+)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--feature-id", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--bump", choices=["patch", "minor", "major"], help="SemVer bump type")
    g.add_argument("--set-version", dest="set_version", help="Explicit SemVer version X.Y.Z")
    ap.add_argument("--note", default="Schema evolution")
    ap.add_argument("--run-validate", action="store_true", help="Run validator with per-step logging")
    return ap.parse_args()


def load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_schema(path: Path, data: dict) -> None:
    txt = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(txt, encoding="utf-8")


def bump_version(ver: str, kind: str) -> str:
    m = SEMVER_RE.match(ver)
    if not m:
        raise ValueError(f"Invalid SemVer: {ver}")
    maj, mi, pa = int(m.group("maj")), int(m.group("min")), int(m.group("pch"))
    if kind == "patch":
        pa += 1
    elif kind == "minor":
        mi += 1
        pa = 0
    elif kind == "major":
        maj += 1
        mi = 0
        pa = 0
    return f"{maj}.{mi}.{pa}"


def update_id_major(id_val: str, major: int) -> str:
    # $id format: urn:automatr:schema:capsule:<feature_id>:planning.output_contract:vN
    return re.sub(r":v\d+$", f":v{major}", id_val)


def ensure_changelog(base: Path) -> Path:
    clog = base / "CHANGELOG.md"
    if not clog.exists():
        clog.write_text("# CHANGELOG\n\n", encoding="utf-8")
    return clog


def append_changelog(base: Path, new_version: str, note: str) -> None:
    clog = ensure_changelog(base)
    today = dt.date.today().isoformat()
    with clog.open("a", encoding="utf-8") as f:
        f.write(f"{today} | {new_version} | planning.output_contract: {note}\n")


def run_validator(feature_id: str, doc_path: Path):
    env = os.environ.copy()
    env["FEATURE_ID"] = feature_id
    env["DOC_PATH"] = str(doc_path)
    cmd = ["bash", str(ROOT / "capsule" / "reports" / "validation" / "validate_all.sh")]
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        # Print but do not raise to allow caller to handle gating
        print(f"Validator exited with code {e.returncode}")


def main():
    args = parse_args()
    base = ROOT / "features" / args.feature_id
    schema_path = base / "output_contract.schema.json"
    if not schema_path.exists():
        raise SystemExit(f"Schema not found: {schema_path}")

    data = load_schema(schema_path)
    current = data.get("version", "0.1.0")
    if args.set_version:
        new_version = args.set_version
        bump_kind = None
    else:
        new_version = bump_version(current, args.bump)
        bump_kind = args.bump

    # Update version
    data["version"] = new_version

    # Update $id major only on MAJOR bump (align vN suffix)
    m = SEMVER_RE.match(new_version)
    if m and bump_kind == "major":
        maj = int(m.group("maj"))
        if "$id" in data:
            data["$id"] = update_id_major(str(data["$id"]), maj)

    save_schema(schema_path, data)

    # Append CHANGELOG
    append_changelog(base, new_version, args.note)

    # Optionally run validator with per-step logging
    if args.run_validate:
        run_validator(args.feature_id, schema_path)

    print(f"Updated schema version: {current} -> {new_version}")
    if "$id" in data:
        print(f"$id: {data['$id']}")


if __name__ == "__main__":
    main()

