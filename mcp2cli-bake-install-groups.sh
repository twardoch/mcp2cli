#!/usr/bin/env bash
# mcp2cli-bake-install-groups.sh — auto-create and install baked configs for
# every tool-name prefix found in an MCP server's tool list.
#
# Usage: mcp2cli-bake-install-groups.sh <mcp-url>
#
# Tool names that contain '--' are assumed to follow the convention
# "<group>--<action>".  For each unique <group> the script:
#   1. Creates a baked config that includes only that group's tools.
#   2. Installs a shell wrapper for it.
#
# Override the mcp2cli binary with MCP2CLI_BIN (default: mcp2cli).

set -euo pipefail

MCP_URL="${1:?Usage: $0 <mcp-url>}"
MCP2CLI_BIN="${MCP2CLI_BIN:-mcp2cli}"

# List all tools in compact (space-separated) form
tools=$("$MCP2CLI_BIN" --mcp "$MCP_URL" --compact)

# Derive unique group prefixes from tool names containing '--'
groups=$(printf '%s\n' $tools | grep -- '--' | sed 's/--.*$//' | sort -u)

if [ -z "$groups" ]; then
    echo "No group prefixes found (no tool names containing '--')."
    exit 0
fi

echo "Found the following unique group name(s):"
for g in $groups; do
    echo "- $g"
done

for g in $groups; do
    "$MCP2CLI_BIN" bake create "$g" --mcp "$MCP_URL" --include "${g}--*" --force
    "$MCP2CLI_BIN" bake install "$g"
done
