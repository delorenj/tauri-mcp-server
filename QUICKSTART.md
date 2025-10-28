# Quick Start: Publishing Guide

## One-Time Setup

```bash
# 1. Install Python dependencies
pip install -r requirements-publish.txt

# Or use make
make setup-publish

# 2. Login to npm
npm login
```

## Quick Commands

### Using the Python Script Directly

```bash
# Publish plugin with patch bump (0.1.0 → 0.1.1)
./publish.py plugin --bump patch

# Publish MCP server with minor bump (0.2.0 → 0.3.0)
./publish.py mcp --bump minor

# Publish both with major bump
./publish.py all --bump major

# Dry run to preview changes
./publish.py all --bump patch --dry-run
```

### Using Make (Easier)

```bash
# See all available commands
make help

# Publish plugin with patch bump
make publish-plugin-patch

# Publish MCP server with minor bump
make publish-mcp-minor

# Publish both with patch bump
make publish-all-patch

# Dry run
make dry-run-all
```

## Version Bumping

- `--bump patch`: 0.1.0 → 0.1.1 (bug fixes)
- `--bump minor`: 0.1.0 → 0.2.0 (new features)
- `--bump major`: 0.1.0 → 1.0.0 (breaking changes)

## Flags

- `--dry-run` - Preview without publishing
- `--skip-build` - Skip build step
- `-d` - Short for --dry-run
- `-s` - Short for --skip-build
- `-b` - Short for --bump

## Examples

```bash
# Preview a patch release
./publish.py plugin -b patch -d

# Publish without rebuilding
./publish.py mcp -b patch -s

# Quick publish both packages (patch)
make publish-all-patch
```

## After Publishing

```bash
# Push git tags
git push --tags

# Commit version changes
git add package.json mcp-server-ts/package.json
git commit -m "chore: bump versions"
git push
```

## Troubleshooting

**"Not logged in to npm"**
```bash
npm login
```

**"Build failed"**
```bash
npm install
cd mcp-server-ts && npm install
```

For more details, see [docs/PUBLISHING.md](docs/PUBLISHING.md)
