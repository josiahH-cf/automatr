#!/usr/bin/env bash
set -euo pipefail

if [[ ${1-} == "" ]]; then
  echo "Usage: $0 <version>" >&2
  exit 2
fi

VERSION="$1"
# SemVer 2.0.0 with optional pre-release and build metadata
REGEX='^([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'

if [[ "$VERSION" =~ $REGEX ]]; then
  echo "OK: version '$VERSION' is valid SemVer"
  exit 0
else
  echo "ERROR: invalid SemVer '$VERSION' (expected MAJOR.MINOR.PATCH with optional -pre and +build)" >&2
  exit 1
fi

