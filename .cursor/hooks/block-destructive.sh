#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
cmd="$(printf '%s' "$payload" | jq -r '.command // empty')"

dangerous='rm[[:space:]].*(-r|-rf|--recursive)|mkfs|dd[[:space:]].*if=|shutdown|reboot|:(){:|:&};:|kubectl[[:space:]]+delete|docker[[:space:]]+system[[:space:]]+prune'

if printf '%s' "$cmd" | grep -Eq "$dangerous"; then
  jq -n \
    --arg msg "Blocked potentially destructive command: $cmd" \
    '{continue: true, permission: "deny", user_message: $msg, agent_message: $msg}'
else
  jq -n '{continue: true, permission: "allow"}'
fi