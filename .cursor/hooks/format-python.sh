#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
file="$(printf '%s' "$payload" | jq -r '.file_path // .filePath // empty')"

case "$file" in
  *.py)
    if command -v uv >/dev/null 2>&1; then
      uv run ruff format "$file" || true
    else
      ruff format "$file" || true
    fi
    ;;
esac

printf '{}\n'