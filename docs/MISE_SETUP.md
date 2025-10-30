# Mise Environment Setup for Tauri MCP Server

This project uses [mise](https://mise.jdx.dev/) to automatically manage the Tauri MCP SSE server when you enter the project directory.

## Features

### 🚀 **Auto-Start Server**
When you `cd` into the project directory, mise automatically:
- Builds the MCP server if needed
- Starts the SSE server on port 8467
- Shows the endpoint URL for Claude Code configuration

### 🛑 **Smart Server Management**
- Detects if server is already running
- Manages PID files and logs
- Provides helpful status information

### 📋 **Convenient Commands**
All server management through simple mise tasks:

```bash
mise run mcp:start    # Start the SSE server
mise run mcp:stop     # Stop the SSE server  
mise run mcp:restart  # Restart the server
mise run mcp:status   # Check server status
mise run mcp:logs     # View server logs
```

## Environment Variables

The following environment variables are automatically set:

```bash
TAURI_MCP_SSE_PORT=8467              # SSE server port
TAURI_MCP_SSE_HOST=127.0.0.1         # SSE server host
TAURI_MCP_PIDFILE=.mise/tauri-mcp-server.pid  # PID file location
```

## Directory Hooks

### Enter Hook (`.mise/hooks/enter`)
Automatically runs when you `cd` into the directory:
- Checks if server is running
- Starts server if not running
- Shows helpful configuration information

### Leave Hook (`.mise/hooks/leave`)
Runs when you `cd` out of the directory:
- Shows reminder if server is still running
- Optionally auto-stops server (if `TAURI_MCP_AUTO_STOP=true`)

## Usage Examples

### Basic Usage
```bash
# Enter the directory (auto-starts server)
cd /path/to/tauri-mcp-server

# Check status
mise run mcp:status

# View logs
mise run mcp:logs
```

### Claude Code Integration
```bash
# Easy one-command setup
mise run mcp:configure-claude

# Or manually:
claude mcp add tauri-mcp "$(pwd)/scripts/tauri-mcp-wrapper.sh"
```

### Advanced Configuration
```bash
# Enable auto-stop when leaving directory
export TAURI_MCP_AUTO_STOP=true

# Use custom port
export TAURI_MCP_SSE_PORT=9000
mise run mcp:restart
```

## File Structure

```
.mise/
├── hooks/
│   ├── enter          # Auto-start hook
│   └── leave          # Auto-stop hook
├── tauri-mcp-server.pid   # Server PID file
└── tauri-mcp-server.log   # Server logs
```

## Troubleshooting

### Server Won't Start
```bash
# Check logs
mise run mcp:logs

# Force restart
mise run mcp:stop
mise run mcp:start
```

### Port Already in Use
```bash
# Change port
export TAURI_MCP_SSE_PORT=9000
mise run mcp:restart
```

### Clean Reset
```bash
# Stop server and clean files
mise run mcp:stop
rm -f .mise/tauri-mcp-server.*
mise run mcp:start
```

## Benefits

1. **Zero Configuration**: Just `cd` into the directory and everything works
2. **Development Friendly**: Automatic rebuilds when source changes
3. **Resource Efficient**: Only runs when you're working in the project
4. **Easy Integration**: Perfect for Claude Code SSE transport
5. **Transparent**: All operations are logged and visible
