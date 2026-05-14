#!/usr/bin/env bash
# Cursor `beforeMCPExecution` hook. Audits every MCP tool call, optionally
# blocks tools whose names look write-capable. failClosed is FALSE in
# hooks.json, so on script error we default to "allow".
set -uo pipefail

DEFAULT_ALLOW='{"continue":true,"permission":"allow"}'
HOOK_OUTPUT=""
trap 'printf "%s\n" "${HOOK_OUTPUT:-$DEFAULT_ALLOW}"' EXIT

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$HOOK_DIR/_common.sh" ]] && {
  # shellcheck source=/dev/null
  source "$HOOK_DIR/_common.sh" 2>/dev/null || true
}

payload="$(cat 2>/dev/null || printf '{}')"
server="$(printf '%s' "$payload" | jq -r '.server_name // .serverName // .server // "unknown-server"' 2>/dev/null || printf 'unknown-server')"
tool="$(printf '%s' "$payload" | jq -r '.tool_name // .toolName // .tool // .name // "unknown-tool"' 2>/dev/null || printf 'unknown-tool')"
timestamp="$(date -u +'%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || printf 'unknown-time')"

# Best-effort audit log: prefer repo .cursor/logs, fall back to /tmp.
log_dir=""
if [[ -n "${REPO_ROOT:-}" ]] && mkdir -p "${REPO_ROOT}/.cursor/logs" 2>/dev/null; then
  log_dir="${REPO_ROOT}/.cursor/logs"
else
  fb="${TMPDIR:-/tmp}/inference-sandbox-cursor-logs-${USER:-unknown}"
  mkdir -p "$fb" 2>/dev/null && log_dir="$fb"
fi
if [[ -n "$log_dir" ]]; then
  printf '%s' "$payload" \
    | jq -c --arg ts "$timestamp" --arg s "$server" --arg t "$tool" \
        '{ts:$ts, server:$s, tool:$t, payload:.}' 2>/dev/null \
    >> "$log_dir/mcp-audit.log" 2>/dev/null || true
fi

# Block tools whose names match a write-side verb anchored on _ or word edge.
# This avoids the previous false positives on read tools that merely contain
# words like "pull" or "issue". Adjust as needed when real names are observed.
DENY_PATTERN='(^|_)(create|update|delete|merge|push|write|add|remove|patch|put|set|destroy|drop|reset)(_|$)'

if printf '%s' "$tool" | grep -Eqi "$DENY_PATTERN"; then
  msg="Blocked write-capable MCP call: server=${server} tool=${tool}. Edit DENY_PATTERN in .cursor/hooks/audit-mcp.sh to relax."
  HOOK_OUTPUT="$(jq -cn --arg msg "$msg" \
    '{continue: true, permission: "deny", user_message: $msg, agent_message: $msg}' 2>/dev/null)" || HOOK_OUTPUT=""
fi
