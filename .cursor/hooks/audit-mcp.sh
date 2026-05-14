#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"

mkdir -p .cursor/logs

timestamp="$(date -Iseconds)"

server="$(printf '%s' "$payload" | jq -r '.server_name // .serverName // .server // "unknown-server"')"
tool="$(printf '%s' "$payload" | jq -r '.tool_name // .toolName // .name // "unknown-tool"')"

printf '%s server=%s tool=%s payload=%s\n' \
  "$timestamp" "$server" "$tool" "$payload" >> .cursor/logs/mcp-audit.log

# Block obviously write-capable GitHub-style actions by default.
# Adjust this list once you see the real tool names in .cursor/logs/mcp-audit.log.
if printf '%s %s' "$server" "$tool" | grep -Eiq 'github.*(create|update|delete|merge|comment|review|issue|pull|push|write)'; then
  jq -n \
    --arg msg "Blocked write-capable MCP call: server=$server tool=$tool. Review manually or relax audit-mcp.sh." \
    '{continue: true, permission: "deny", user_message: $msg, agent_message: $msg}'
  exit 0
fi

jq -n '{continue: true, permission: "allow"}'