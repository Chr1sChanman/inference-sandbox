#!/usr/bin/env bash
# Cursor `afterFileEdit` hook. Runs `ruff format` on the saved Python file.
set -uo pipefail
trap 'printf "{}\n"' EXIT

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$HOOK_DIR/_common.sh" ]] || exit 0
# shellcheck source=/dev/null
source "$HOOK_DIR/_common.sh" || exit 0

payload="$(cat 2>/dev/null)" || exit 0
file="$(printf '%s' "$payload" | jq -r '.file_path // .filePath // empty' 2>/dev/null)" || exit 0

[[ "$file" =~ \.[Pp][Yy]$ ]] || exit 0
[[ "$file" != /* ]] && file="${REPO_ROOT}/${file}"
[[ -f "$file" ]] || exit 0

pick_project_python || exit 0
"${PROJECT_PYTHON_CMD[@]}" -m ruff format "$file" >/dev/null || true
