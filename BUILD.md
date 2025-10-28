# Build System Documentation

This project uses a modern Python-based build system (`build.py`) to manage the compilation of both the Tauri plugin (Rust) and MCP server (TypeScript).

## Prerequisites

### Required Tools

- **Python 3.12+** - Build script runtime
- **Rust & Cargo** - For building the Tauri plugin
- **Bun or npm** - For building TypeScript components

### Installing Python Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -r requirements.txt
```

## Quick Start

```bash
# Build everything (plugin + MCP server)
python build.py all

# Build with clean artifacts and verbose output
python build.py all --clean --verbose

# Build only the Rust plugin
python build.py plugin

# Build only the MCP server
python build.py mcp
```

## Commands

### `build.py plugin`

Builds the Rust Tauri plugin and JavaScript bindings.

**Options:**
- `--clean, -c` - Remove `target/` and `dist-js/` directories before building
- `--verbose, -v` - Show detailed build output with real-time command output
- `--release, -r` - Build in release mode with optimizations (default: True)
- `--target, -t <TRIPLE>` - Specify Rust target triple (e.g., `x86_64-unknown-linux-gnu`)

**Examples:**
```bash
# Standard release build
python build.py plugin

# Clean build with verbose output
python build.py plugin --clean --verbose

# Build for specific target
python build.py plugin --target aarch64-apple-darwin

# Debug build (not optimized)
python build.py plugin --no-release
```

**What it builds:**
1. Rust library via `cargo build`
2. JavaScript bindings via `bun run build` (or `npm run build`)
3. Output: `target/release/` and `dist-js/`

---

### `build.py mcp`

Builds the TypeScript MCP server.

**Options:**
- `--clean, -c` - Remove `mcp-server-ts/build/` directory before building
- `--verbose, -v` - Show detailed build output with real-time command output

**Examples:**
```bash
# Standard build
python build.py mcp

# Clean build with verbose output
python build.py mcp --clean --verbose
```

**What it builds:**
1. TypeScript compilation via `bun run build` (or `npm run build`)
2. Output: `mcp-server-ts/build/`

---

### `build.py all`

Builds both the plugin and MCP server in sequence.

**Options:**
- `--clean, -c` - Clean all build artifacts before building
- `--verbose, -v` - Show detailed build output for all stages
- `--release, -r` - Build plugin in release mode (default: True)
- `--target, -t <TRIPLE>` - Specify Rust target triple for plugin build

**Examples:**
```bash
# Build everything
python build.py all

# Clean build with verbose output
python build.py all --clean --verbose

# Build for production deployment
python build.py all --clean --release
```

**Build order:**
1. Tauri plugin (Rust + JS bindings)
2. MCP server (TypeScript)

---

## Build Artifacts

### Plugin Artifacts

| Path | Description |
|------|-------------|
| `target/debug/` | Debug build of Rust library |
| `target/release/` | Optimized release build of Rust library |
| `dist-js/` | Compiled JavaScript bindings and TypeScript definitions |

### MCP Server Artifacts

| Path | Description |
|------|-------------|
| `mcp-server-ts/build/` | Compiled JavaScript from TypeScript |

---

## Features

### ✨ Modern Python Features

- **Python 3.12+ syntax** - Uses latest language features
- **Type hints throughout** - Complete type safety with mypy compatibility
- **Pathlib for paths** - Cross-platform path handling
- **Rich terminal output** - Beautiful console UI with progress indicators

### 🎨 Beautiful Output

The build script uses [Rich](https://github.com/Textualize/rich) for:
- Colored output with semantic meaning
- Spinners for long-running operations
- Build configuration tables
- Bordered panels for status messages
- Real-time command output in verbose mode

### 🛡️ Error Handling

- **Tool validation** - Checks for required commands before building
- **Proper exit codes** - Returns appropriate codes for CI/CD integration
- **Detailed error messages** - Shows command output on failure
- **Keyboard interrupt handling** - Clean exit on Ctrl+C

### 🔧 Cross-Platform Support

- Uses `pathlib` for OS-agnostic path handling
- Detects available package managers (bun/npm)
- Works on Linux, macOS, and Windows

---

## CI/CD Integration

The build script is designed for use in automated workflows:

```yaml
# Example GitHub Actions workflow
- name: Install Python dependencies
  run: pip install -r requirements.txt

- name: Build project
  run: python build.py all --release

- name: Check build succeeded
  run: |
    test -f target/release/libtauri_plugin_mcp_gui.so
    test -d mcp-server-ts/build
```

**Exit codes:**
- `0` - Build successful
- `1` - Build failed
- `130` - User interrupted (Ctrl+C)

---

## Troubleshooting

### "Missing required tools" error

Install the missing tools:

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Bun
curl -fsSL https://bun.sh/install | bash
```

### "Command not found: cargo/bun"

Ensure tools are in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.cargo/bin:$PATH"
export PATH="$HOME/.bun/bin:$PATH"
```

### Build fails with verbose output

Run with `--verbose` to see detailed output:

```bash
python build.py all --verbose
```

### Permission denied

Make the script executable:

```bash
chmod +x build.py
./build.py all
```

---

## Development Workflow

### Typical workflow for development:

```bash
# Initial build
python build.py all --clean

# After Rust changes
python build.py plugin

# After TypeScript changes
python build.py mcp

# Before committing
python build.py all --clean --release
```

### For testing cross-platform builds:

```bash
# Build for Linux
python build.py plugin --target x86_64-unknown-linux-gnu

# Build for macOS (Intel)
python build.py plugin --target x86_64-apple-darwin

# Build for macOS (Apple Silicon)
python build.py plugin --target aarch64-apple-darwin

# Build for Windows
python build.py plugin --target x86_64-pc-windows-msvc
```

---

## Script Architecture

```
build.py
├── Command validation (check_command_exists)
├── Tool validation (validate_tools)
├── Command execution (run_command)
├── Directory cleaning (clean_directory)
├── Build functions
│   ├── build_plugin() - Rust + JS
│   └── build_mcp() - TypeScript
└── CLI commands (Typer)
    ├── plugin
    ├── mcp
    └── all
```

**Design principles:**
- Single responsibility functions
- Comprehensive error handling
- Beautiful user feedback
- CI/CD friendly
- Cross-platform compatible

---

## Contributing

When adding new build steps:

1. Add a new function for the build logic
2. Update the appropriate command (plugin/mcp/all)
3. Add validation for any new tools required
4. Update this documentation
5. Test on multiple platforms

---

## License

Same as parent project (MIT)
