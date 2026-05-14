#!/usr/bin/env bash
# Cursor `stop` hook. Runs the project's fast tests; surfaces output only on
# failure. Stdout is reserved for the hook's JSON contract -> always `{}`.
set -uo pipefail
trap 'printf "{}\n"' EXIT

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$HOOK_DIR/_common.sh" ]] || exit 0
# shellcheck source=/dev/null
source "$HOOK_DIR/_common.sh" || exit 0

PYTEST_ARGS=( -q -x -m "not gpu and not k8s and not slow" )

pick_project_python || exit 0

TMP_OUT="$(mktemp 2>/dev/null)" || exit 0
trap 'rm -f "$TMP_OUT"; printf "{}\n"' EXIT

"${PROJECT_PYTHON_CMD[@]}" -m pytest "${PYTEST_ARGS[@]}" >"$TMP_OUT" 2>&1
rc=$?

if (( rc != 0 )); then
  {
    printf 'quick-tests.sh: pytest exited with code %d\n' "$rc"
    cat "$TMP_OUT"
  } >&2
fi
