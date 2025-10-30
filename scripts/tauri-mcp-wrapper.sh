#!/bin/bash
# Wrapper script for Tauri MCP Server to work around PATH issues in Claude Code
# This script auto-detects npx location and uses the full path to avoid ENOENT errors

set -euo pipefail

# Function to find npx
find_npx() {
    # Try common locations
    local npx_paths=(
        "/home/delorenj/.local/share/mise/installs/node/24.6.0/bin/npx"
        "/home/delorenj/.local/share/mise/installs/node/latest/bin/npx"
        "$(command -v npx 2>/dev/null || true)"
        "/usr/local/bin/npx"
        "/usr/bin/npx"
    )

    for path in "${npx_paths[@]}"; do
        if [[ -n "$path" && -x "$path" ]]; then
            echo "$path"
            return 0
        fi
    done

    return 1
}

# Find npx
NPX_PATH=$(find_npx)

if [[ -z "$NPX_PATH" ]]; then
    echo "Error: npx not found in any common locations" >&2
    echo "Please ensure Node.js is installed and npx is available" >&2
    echo "Tried locations:" >&2
    echo "  - mise installations" >&2
    echo "  - system PATH" >&2
    echo "  - /usr/local/bin/npx" >&2
    echo "  - /usr/bin/npx" >&2
    exit 1
fi

# Log the npx path for debugging
echo "Using npx at: $NPX_PATH" >&2

# Execute the MCP server with full path
exec "$NPX_PATH" -y @delorenj/tauri-mcp-server@latest "$@"
