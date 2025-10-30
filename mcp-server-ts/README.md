# Tauri MCP Server

A Model Context Protocol (MCP) server that enables AI agents to interact with Tauri desktop applications through standardized interfaces.

## Features

- **Screenshot Capture**: Take screenshots of Tauri windows
- **DOM Access**: Retrieve HTML content from webview windows  
- **Mouse Control**: Simulate mouse clicks, movements, and scrolling
- **Text Input**: Send text input to focused elements
- **JavaScript Execution**: Run arbitrary JavaScript in application context
- **Local Storage Management**: Get, set, remove, and clear localStorage entries
- **Window Management**: Control window position, size, focus, and state

## Installation

```bash
npm install -g tauri-mcp-server
```

## Usage

The server supports two transport methods:

### Transport Options

#### 1. Stdio Transport (Default)
```bash
# Run with stdio transport (default)
tauri-mcp-server

# Or explicitly specify stdio
tauri-mcp-server --transport stdio
```

#### 2. SSE Transport (Server-Sent Events)
```bash
# Run with SSE transport on default port 8467
tauri-mcp-server --transport sse

# Run with SSE on custom port
tauri-mcp-server --transport sse --port 9000

# Run with SSE on custom host and port
tauri-mcp-server --transport sse --host 0.0.0.0 --port 8467
```

### With Claude Desktop

#### Stdio Transport Configuration
Add to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "tauri-mcp": {
      "command": "tauri-mcp-server"
    }
  }
}
```

#### SSE Transport Configuration
For SSE transport, configure as an HTTP server:

```json
{
  "mcpServers": {
    "tauri-mcp": {
      "url": "http://127.0.0.1:8467/sse"
    }
  }
}
```

Then start the server separately:
```bash
tauri-mcp-server --transport sse
```

### With Cursor

Add to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "tauri-mcp": {
      "command": "npx",
      "args": ["tauri-mcp-server"]
    }
  }
}
```

## Available Tools

- `take_screenshot` - Capture window screenshots
- `get_dom` - Retrieve DOM content from webviews
- `mouse_movement` - Control mouse cursor and clicks
- `text_input` - Send text to focused elements
- `execute_js` - Run JavaScript in application context
- `manage_local_storage` - Handle localStorage operations
- `manage_window` - Control window properties
- `get_element_position` - Find element positions for interaction
- `send_text_to_element` - Send text to specific elements

## Requirements

- Node.js 18+
- A Tauri application with the MCP plugin installed

## Architecture

The server communicates with Tauri applications through:
- IPC (Unix sockets/named pipes) for local communication
- TCP sockets for network communication
- Direct Tauri API integration

## License

MIT - See [LICENSE](../LICENSE) for details.

## Repository

https://github.com/delorenj/tauri-plugin-mcp
