#!/usr/bin/env bash
set -euo pipefail

if [[ ${1-} == "" ]]; then
  echo "Usage: $0 <feature_id>" >&2
  exit 2
fi

FEATURE_ID="$1"
# kebab-case; optional -vN suffix
REGEX='^[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:-v[0-9]+)?$'

if [[ "$FEATURE_ID" =~ $REGEX ]]; then
  echo "OK: feature_id '$FEATURE_ID' is valid"
  exit 0
else
  echo "ERROR: invalid feature_id '$FEATURE_ID' (expected kebab-case, optional -vN)" >&2
  exit 1
fi

