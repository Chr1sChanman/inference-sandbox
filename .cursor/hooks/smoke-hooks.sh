#!/usr/bin/env bash
# Local verification for Cursor hooks. Run from anywhere:
#   bash .cursor/hooks/smoke-hooks.sh
# Set SMOKE_SKIP_PYTEST=1 to skip the (slow) quick-tests step.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOOKS="${REPO}/.cursor/hooks"
cd "$REPO" || exit 1

step() { printf '\n=== %s ===\n' "$*"; }
fail() { printf '!! FAIL: %s\n' "$*" >&2; exit 1; }

run_hook() {
  # $1 = hook script, stdin = payload, prints stdout. Stderr is dropped to
  # keep smoke output readable; rerun the hook directly if stderr is needed.
  bash "$1" 2>/dev/null
}

step "syntax check (.sh)"
for f in "$HOOKS"/*.sh; do
  bash -n "$f" || fail "syntax error: $f"
  printf '  ok %s\n' "${f#"$REPO"/}"
done

step "block-destructive: allow safe command"
echo '{"command":"ls -la"}' | run_hook "$HOOKS/block-destructive.sh" \
  | jq -e '.permission == "allow"' >/dev/null \
  || fail "block-destructive denied a safe command"

step "block-destructive: deny destructive commands"
deny_cases=(
  'rm -rf /tmp/foo'
  'rm -fr ./build'
  'mkfs.ext4 /dev/sdb1'
  'kubectl delete pods --all'
  'docker system prune -af'
  'git push origin main --force'
  'chmod -R 777 /'
  'shutdown -h now'
  'find / -name foo -delete'
)
for c in "${deny_cases[@]}"; do
  out="$(jq -cn --arg c "$c" '{command:$c}' | run_hook "$HOOKS/block-destructive.sh")"
  perm="$(printf '%s' "$out" | jq -r '.permission // "missing"')"
  [[ "$perm" == "deny" ]] || fail "expected deny for: $c (got $perm)"
done
printf '  ok %d destructive cases\n' "${#deny_cases[@]}"

step "block-destructive: avoid false positives"
allow_cases=(
  'cat /etc/shutdown.conf'
  'echo "mkfs is dangerous"'
  'grep -r reboot ./docs'
  'git push origin main'
  'rm somefile.txt'
)
for c in "${allow_cases[@]}"; do
  out="$(jq -cn --arg c "$c" '{command:$c}' | run_hook "$HOOKS/block-destructive.sh")"
  perm="$(printf '%s' "$out" | jq -r '.permission // "missing"')"
  [[ "$perm" == "allow" ]] || fail "false positive on: $c (got $perm)"
done
printf '  ok %d safe cases\n' "${#allow_cases[@]}"

step "audit-mcp: allow read tools"
read_cases=(
  '{"server":"github","tool":"get_pull_request"}'
  '{"server":"github","tool":"list_issues"}'
  '{"server":"github","tool":"search_repositories"}'
)
for p in "${read_cases[@]}"; do
  perm="$(echo "$p" | run_hook "$HOOKS/audit-mcp.sh" | jq -r '.permission')"
  [[ "$perm" == "allow" ]] || fail "audit-mcp wrongly denied: $p"
done

step "audit-mcp: deny write tools"
write_cases=(
  '{"server":"github","tool":"create_issue"}'
  '{"server":"github","tool":"delete_branch"}'
  '{"server":"github","tool":"merge_pull_request"}'
)
for p in "${write_cases[@]}"; do
  perm="$(echo "$p" | run_hook "$HOOKS/audit-mcp.sh" | jq -r '.permission')"
  [[ "$perm" == "deny" ]] || fail "audit-mcp wrongly allowed: $p"
done

step "format-python: emits {}"
out="$(echo '{"file_path":"src/inference_sandbox/__init__.py"}' | run_hook "$HOOKS/format-python.sh")"
[[ "$out" == "{}" ]] || fail "format-python stdout was: $out"

if [[ "${SMOKE_SKIP_PYTEST:-}" != "1" ]]; then
  step "quick-tests: emits exactly {} on stdout"
  out="$(bash "$HOOKS/quick-tests.sh" 2>/dev/null)"
  [[ "$out" == "{}" ]] || fail "quick-tests stdout was: $out"
fi

printf '\nsmoke-hooks.sh: ALL OK\n'
