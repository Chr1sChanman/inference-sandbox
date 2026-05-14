#!/usr/bin/env bash
# Cursor `beforeShellExecution` hook. failClosed is TRUE in hooks.json: any
# script error blocks ALL shell commands. Keep this file minimal and robust;
# do not install a recovery trap.
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$HOOK_DIR/_common.sh" ]]; then
  # shellcheck source=/dev/null
  source "$HOOK_DIR/_common.sh" || true
fi

payload="$(cat)"
cmd="$(printf '%s' "$payload" | jq -r '.command // empty')"

# "Command-start" boundary: start of string, or after a shell separator that
# begins a new command (; | & ( ). Plain whitespace alone does NOT qualify, so
# arguments like `grep -r reboot ./docs` are not mistaken for the command name.
CMD_START='(^|[;|&(][[:space:]]*)'

# Parallel arrays: name -> regex. The deny message includes the rule name.
DENY_NAMES=(
  rm-recursive
  mkfs
  dd-to-block-device
  system-power
  init-runlevel
  fork-bomb
  kubectl-delete
  docker-prune
  git-force-push
  chmod-recursive-root
  find-delete
  redirect-to-block-device
)
DENY_PATTERNS=(
  "${CMD_START}rm[[:space:]]+([^[:space:]]+[[:space:]]+)*-[A-Za-z]*[Rr]"
  "${CMD_START}mkfs([._-][a-z0-9.]+)?([[:space:];|&]|$)"
  "${CMD_START}dd[[:space:]].*of=/dev/(sd|nvme|hd|vd|mmc|loop|md)"
  "${CMD_START}(shutdown|halt|poweroff|reboot)([[:space:]]|$)"
  "${CMD_START}init[[:space:]]+[06]([[:space:]]|$)"
  ':[[:space:]]*\(\)[[:space:]]*\{[[:space:]]*:[[:space:]]*\|[[:space:]]*:[[:space:]]*&'
  "${CMD_START}kubectl[[:space:]]+delete([[:space:]]|$)"
  "${CMD_START}docker[[:space:]]+system[[:space:]]+prune"
  "${CMD_START}git[[:space:]]+push[[:space:]]+.*(--force([[:space:]]|$)|-f([[:space:]]|$))"
  "${CMD_START}chmod[[:space:]]+(-R|--recursive)[[:space:]]+[0-9]+[[:space:]]+/([[:space:]]|$)"
  "${CMD_START}find[[:space:]]+(/|\\.)[^[:space:]]*[[:space:]].*-delete"
  '>[[:space:]]*/dev/(sd[a-z]|nvme[0-9]|hd[a-z]|vd[a-z])'
)

for i in "${!DENY_PATTERNS[@]}"; do
  if printf '%s' "$cmd" | grep -Eq "${DENY_PATTERNS[$i]}"; then
    name="${DENY_NAMES[$i]}"
    msg="Blocked destructive command [${name}]: ${cmd}"
    jq -n --arg msg "$msg" \
      '{continue: true, permission: "deny", user_message: $msg, agent_message: $msg}'
    exit 0
  fi
done

jq -n '{continue: true, permission: "allow"}'
