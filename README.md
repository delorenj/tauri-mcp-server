# Tauri Plugin: Model Context Protocol (MCP)

A Tauri plugin and MCP server that enables AI agents (Claude Code, Cursor, etc.) to interact with and debug Tauri desktop applications through standardized interfaces.

**Author:** Jarad DeLorenzo ([@delorenj](https://github.com/delorenj))
**Repository:** https://github.com/delorenj/tauri-plugin-mcp
**Homepage:** https://delorenj.github.io

### Features

The Tauri MCP Plugin provides a comprehensive set of tools that allow AI models and external applications to interact with Tauri applications:

#### Window Interaction
- **Take Screenshot**: Capture images of any Tauri window with configurable quality and size
- **Window Management**: Control window position, size, focus, minimize/maximize state
- **DOM Access**: Retrieve the HTML DOM content from webviews windows

#### User Input Simulation
- **Mouse Movement**: Simulate mouse clicks, movements, and scrolling
- **Text Input**: Programmatically input text into focused elements
- **Execute JavaScript**: Run arbitrary JavaScript code in the application context

#### Data & Storage
- **Local Storage Management**: Get, set, remove, and clear localStorage entries
- **Ping**: Simple connectivity testing to verify the plugin is responsive

## Quick Start

### Prerequisites

- **Python 3.12+** - For the build script
- **Rust & Cargo** - For building the Tauri plugin
- **Bun or npm** - For building TypeScript components

### Building the Project

This project uses a modern Python build system for managing both artifacts:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Build everything (recommended)
python build.py all

# Or build individually
python build.py plugin  # Build Rust plugin + JS bindings
python build.py mcp     # Build TypeScript MCP server
```

For detailed build options and documentation, see [BUILD.md](./BUILD.md).

### Legacy Build Commands

If you prefer manual builds:

```bash
# Plugin
bun install
bun run build && bun run build-plugin

# MCP Server
cd mcp-server-ts
bun install
bun run build
```

### Basic Configuration

Add to your Claude Code or Cursor MCP settings:

```json
{
  "mcpServers": {
    "tauri-mcp": {
      "command": "node",
      "args": ["/path/to/tauri-plugin-mcp/mcp-server-ts/build/index.js"]
    }
  }
}
```

## Documentation

- **[Setup Guide](./docs/SETUP.md)** - Detailed integration instructions
- **[MCP Server](./docs/MCP_SERVER.md)** - Available tools and configuration
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Common issues and solutions

## Architecture

The plugin uses a multi-layer communication stack:

```
AI Agent (Claude Code/Cursor)
         ↓ (MCP Protocol)
    MCP Server (Node.js)
         ↓ (IPC/TCP Socket)
   Socket Server (Rust)
         ↓ (Tauri APIs)
   Tauri Application
```

Supports both IPC (Unix sockets/named pipes) and TCP connections for maximum flexibility.