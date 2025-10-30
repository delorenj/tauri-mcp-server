# Claude Code Setup for Tauri MCP Server

This guide shows how to set up the Tauri MCP Server with Claude Code, including solutions for common issues.

## Quick Setup

### 1. Automatic Configuration (Recommended)
```bash
# Navigate to the project directory
cd /path/to/tauri-mcp-server

# One-command setup
mise run mcp:configure-claude

# Test the connection
claude mcp list
```

### 2. Manual Configuration
```bash
# Add the MCP server using the wrapper script
claude mcp add tauri-mcp "$(pwd)/scripts/tauri-mcp-wrapper.sh"

# Test the connection
claude mcp list
```

## How It Works

### The Problem
Claude Code runs in an environment where `npx` is not in the PATH, causing `ENOENT` errors when trying to execute:
```bash
npx -y @delorenj/tauri-mcp-server@latest
```

### The Solution
We use a wrapper script (`scripts/tauri-mcp-wrapper.sh`) that:
1. **Auto-detects npx location** - Checks common mise and system locations
2. **Uses full paths** - Avoids PATH dependency issues
3. **Provides clear error messages** - Helps with troubleshooting

## Verification

### Check Connection Status
```bash
claude mcp list
# Should show: tauri-mcp: /path/to/wrapper.sh - ✓ Connected
```

### Check Tauri App Logs
```bash
tail -f /tmp/intelliforia-dev.log
# Should show connection activity when Claude Code connects
```

### Test MCP Server Directly
```bash
# Test the wrapper script
./scripts/tauri-mcp-wrapper.sh
# Should start the MCP server successfully
```

## Troubleshooting

### "No such file or directory" Error
```bash
# Check if the wrapper script exists and is executable
ls -la scripts/tauri-mcp-wrapper.sh

# Make it executable if needed
chmod +x scripts/tauri-mcp-wrapper.sh
```

### "npx not found" Error
```bash
# Check if Node.js/npx is installed
which npx

# If using mise, ensure Node.js is installed
mise install node@latest
```

### Connection Fails
```bash
# Remove and re-add the configuration
claude mcp remove tauri-mcp
mise run mcp:configure-claude

# Check Claude Code debug logs
tail ~/.claude/debug/latest
```

### Tauri App Not Responding
```bash
# Check if Tauri app is running
lsof -i :9999  # Should show intelliforia process

# Check socket file exists
ls -la /tmp/tauri-mcp.sock

# Test socket directly
echo '{"command": "take_screenshot", "payload": {"window_label": "main"}}' | nc -U /tmp/tauri-mcp.sock
```

## Available Tools

Once connected, Claude Code can use these tools:
- `take_screenshot` - Capture application screenshots
- `get_dom` - Extract HTML content from webviews
- `execute_js` - Run JavaScript in application context
- `mouse_movement` - Simulate mouse interactions
- `text_input` - Send text input to elements
- `manage_window` - Control window properties
- `manage_local_storage` - Access localStorage

## Advanced Configuration

### Custom npx Path
Edit `scripts/tauri-mcp-wrapper.sh` to add your specific npx location:
```bash
# Add to the npx_paths array
local npx_paths=(
    "/your/custom/path/to/npx"
    # ... existing paths
)
```

### Different MCP Server Version
```bash
# Modify the wrapper script to use a specific version
exec "$NPX_PATH" -y @delorenj/tauri-mcp-server@0.3.0 "$@"
```

## Benefits of This Approach

1. **Reliable** - Works around Claude Code's PATH limitations
2. **Portable** - Auto-detects npx location across different setups
3. **Debuggable** - Clear error messages and logging
4. **Maintainable** - Single wrapper script to update
5. **Fast** - Uses stdio transport (faster than HTTP/SSE)
