# Publishing Guide

This guide explains how to use the `publish.py` script to publish packages to npm.

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install -r requirements-publish.txt
```

This installs:
- `typer` - Modern CLI framework
- `rich` - Beautiful terminal output

### 2. Configure npm Authentication

Make sure you're logged in to npm:

```bash
npm login
```

### 3. Optional: 1Password CLI Setup

For automatic OTP retrieval, install and configure the 1Password CLI:

```bash
# Install 1Password CLI (example for Linux)
# See: https://developer.1password.com/docs/cli/get-started/

# Sign in to 1Password
op signin

# Verify access to npm OTP
op item get npmjs --vault DeLoSecrets --fields otp
```

If the `op` CLI is not available, the script will skip OTP and you may be prompted to enter it manually during publish.

## Usage

### Basic Commands

The script supports three publish targets:

```bash
# Publish only the Tauri plugin (root package)
./publish.py plugin

# Publish only the MCP server package
./publish.py mcp

# Publish both packages
./publish.py all
```

### Version Bumping

Use the `--bump` flag to automatically increment the version:

```bash
# Patch version (0.1.0 -> 0.1.1)
./publish.py plugin --bump patch

# Minor version (0.1.0 -> 0.2.0)
./publish.py mcp --bump minor

# Major version (0.1.0 -> 1.0.0)
./publish.py all --bump major
```

### Dry Run Mode

Test the publish process without actually publishing:

```bash
# Preview what would happen
./publish.py all --bump patch --dry-run
```

This will:
- Show the version changes
- Build the packages
- Run `npm publish --dry-run` to validate
- NOT modify package.json or create git tags

### Skip Build

If you've already built the packages, skip the build step:

```bash
./publish.py plugin --skip-build
```

### Combined Options

You can combine multiple options:

```bash
# Dry run with version bump and skip build
./publish.py all --bump minor --dry-run --skip-build

# Publish with patch bump, skipping build
./publish.py mcp --bump patch --skip-build
```

## What the Script Does

### Safety Checks

1. **Git Status Check**: Warns if working directory has uncommitted changes
2. **npm Authentication**: Verifies you're logged in to npm
3. **Confirmation Prompt**: Asks for confirmation before publishing

### Version Management

When using `--bump`:
1. Reads current version from `package.json`
2. Increments version according to semver rules
3. Updates `package.json` with new version
4. Creates a git tag (e.g., `v0.2.0`)

### Build Process

Unless `--skip-build` is specified:
1. Runs `npm run build` in the package directory
2. Validates build succeeded before publishing

### 1Password OTP Integration

If 1Password CLI is available:
1. Fetches current OTP from "DeLoSecrets" vault
2. Passes it to `npm publish --otp <code>`
3. Bypasses manual OTP entry

If 1Password CLI is not available:
- Publishes without OTP flag
- npm will prompt for OTP if required by your account

### Publishing

1. Executes `npm publish` (with `--otp` if available)
2. Displays success/failure messages
3. Reminds you to push git tags

## Examples

### Example 1: Release a patch version of the plugin

```bash
./publish.py plugin --bump patch
```

Output:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Publishing Tauri Plugin  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                    Publish Summary
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┓
┃ Package           ┃ Current Version ┃ New Version ┃ Path ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━┩
│ tauri-plugin-mcp  │ 0.1.0           │ 0.1.1       │ .    │
└───────────────────┴─────────────────┴─────────────┴──────┘

BUMP: patch

Logged in to npm as: delorenj
Proceed with publish? [y/N]: y

Retrieved OTP from 1Password
Processing Tauri Plugin...
✓ Updated package.json to version 0.1.1
✓ Created git tag: v0.1.1
✓ Successfully built Tauri Plugin
✓ Successfully published tauri-plugin-mcp@0.1.1

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ All packages published successfully! ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Don't forget to push git tags: git push --tags
```

### Example 2: Dry run to preview changes

```bash
./publish.py all --bump minor --dry-run
```

This shows what would happen without making any changes.

### Example 3: Publish both packages with major version bump

```bash
./publish.py all --bump major
```

This will:
- Bump plugin from 0.1.0 to 1.0.0
- Bump MCP server from 0.2.0 to 1.0.0
- Build both packages
- Publish both to npm
- Create git tags v1.0.0

## After Publishing

### Push Git Tags

After a successful publish, push the git tags to the remote repository:

```bash
git push --tags
```

### Commit package.json Changes

If you bumped versions, commit the updated package.json files:

```bash
git add package.json mcp-server-ts/package.json
git commit -m "chore: bump versions to X.Y.Z"
git push
```

## Troubleshooting

### "Not logged in to npm"

Solution:
```bash
npm login
```

### "Build failed"

Ensure all dependencies are installed:
```bash
npm install
cd mcp-server-ts && npm install
```

### "Could not retrieve OTP from 1Password"

Solutions:
1. Make sure 1Password CLI is installed and signed in
2. Verify the vault name is "DeLoSecrets"
3. Verify the item name is "npmjs"
4. Or continue without OTP (npm will prompt you)

### Git working directory not clean

Either:
1. Commit or stash your changes
2. Use `--dry-run` to test first
3. Confirm you want to continue when prompted

## Help

View all available options:

```bash
./publish.py --help
./publish.py plugin --help
./publish.py mcp --help
./publish.py all --help
```
