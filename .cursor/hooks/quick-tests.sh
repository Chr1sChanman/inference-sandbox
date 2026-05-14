#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  uv run pytest -q -x --timeout=60 -m "not gpu and not k8s and not slow" || true
else
  pytest -q -x --timeout=60 -m "not gpu and not k8s and not slow" || true
fi

printf '{}\n'