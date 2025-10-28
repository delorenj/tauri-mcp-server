# Publishing Workflow

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Runs publish.py                          │
│                 ./publish.py [target] [options]                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────┐
                   │ Parse Arguments │
                   │  • Target       │
                   │  • Bump type    │
                   │  • Flags        │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Load Package(s) │
                   │  • Read JSON    │
                   │  • Get versions │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Display Summary │
                   │  • Table view   │
                   │  • Version info │
                   └────────┬────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   Safety Checks         │
              │                         │
              │  ✓ Git clean?          │
              │  ✓ npm logged in?      │
              │  ✓ User confirms?      │
              └────────┬────────────────┘
                       │ (skip if dry-run)
                       ▼
              ┌─────────────────┐
              │  Get OTP (opt)  │
              │                 │
              │  1Password CLI  │
              │  op item get... │
              └────────┬────────┘
                       │
                       ▼
       ┌───────────────────────────────────┐
       │   FOR EACH PACKAGE               │
       │                                   │
       │   ┌───────────────────────────┐  │
       │   │ 1. Bump Version?          │  │
       │   │    • Calculate new ver    │  │
       │   │    • Update package.json  │  │
       │   │    • Create git tag       │  │
       │   └────────┬──────────────────┘  │
       │            ▼                      │
       │   ┌───────────────────────────┐  │
       │   │ 2. Build Package          │  │
       │   │    • npm run build        │  │
       │   │    • Validate success     │  │
       │   └────────┬──────────────────┘  │
       │            ▼                      │
       │   ┌───────────────────────────┐  │
       │   │ 3. Publish to npm         │  │
       │   │    • npm publish          │  │
       │   │    • With OTP if avail    │  │
       │   │    • Show progress        │  │
       │   └────────┬──────────────────┘  │
       │            ▼                      │
       └────────────┼──────────────────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ Success Report  │
           │  • Versions     │
           │  • Reminder     │
           └─────────────────┘
```

## Detailed Step-by-Step Flow

### Phase 1: Initialization

1. **Script Entry**
   ```bash
   ./publish.py plugin --bump patch
   ```

2. **Argument Parsing** (Typer)
   - Command: `plugin`
   - Options: `--bump=patch`
   - Flags: `--dry-run=False`, `--skip-build=False`

3. **Package Selection**
   ```python
   packages = get_packages(PublishTarget.PLUGIN)
   # Returns: [PackageInfo(name="Tauri Plugin", ...)]
   ```

### Phase 2: Validation & Summary

4. **Load Package Data**
   ```python
   pkg = PackageInfo(...)
   pkg.npm_name  # "tauri-plugin-mcp"
   pkg.version   # "0.1.0"
   ```

5. **Display Summary**
   ```
   ┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
   ┃ Package          ┃ Current    ┃ New        ┃
   ┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
   │ tauri-plugin-mcp │ 0.1.0      │ 0.1.1      │
   └──────────────────┴────────────┴────────────┘
   ```

### Phase 3: Safety Checks (if not dry-run)

6. **Git Status Check**
   ```bash
   git status --porcelain
   # If dirty: warn user, ask confirmation
   ```

7. **npm Authentication**
   ```bash
   npm whoami
   # Output: delorenj ✓
   ```

8. **User Confirmation**
   ```
   Proceed with publish? [y/N]: _
   ```

### Phase 4: OTP Retrieval (if not dry-run)

9. **1Password Integration**
   ```bash
   op item get npmjs --vault DeLoSecrets --fields otp
   # Returns: 123456
   ```
   - If `op` not found → continue without OTP
   - If command fails → continue without OTP
   - If successful → use in publish step

### Phase 5: Package Processing (for each package)

10. **Version Bump** (if --bump specified)
    ```python
    # Current: 0.1.0
    new_version = pkg.bump_version(BumpType.PATCH)
    # New: 0.1.1

    pkg.update_version(new_version)
    # Updates package.json
    ```

11. **Git Tagging** (if version bumped)
    ```bash
    git tag -a v0.1.1 -m "Release v0.1.1"
    ```

12. **Build Package** (unless --skip-build)
    ```bash
    npm run build
    # Executes prepublishOnly hook automatically
    ```

13. **Publish to npm**
    ```bash
    npm publish --otp 123456
    # Or without --otp if not available
    ```

### Phase 6: Completion

14. **Success Report**
    ```
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ All packages published successfully! ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    Don't forget to push git tags: git push --tags
    ```

## Error Handling Flow

```
┌──────────────────┐
│  Any Error       │
│  Occurs          │
└────────┬─────────┘
         │
         ▼
    ┌────────────────────┐
    │ Catch Exception    │
    │                    │
    │ • CalledProcess    │
    │ • FileNotFound     │
    │ • JSONDecode       │
    │ • General          │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ Display Error      │
    │                    │
    │ [red]Error...[/red]│
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ Exit with Code 1   │
    │                    │
    │ raise typer.Exit(1)│
    └────────────────────┘
```

## Dry-Run Flow

When `--dry-run` is specified:

```
┌───────────────────────┐
│ Dry-Run Mode Active   │
└──────────┬────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Skip Safety Checks           │
│  • No git check              │
│  • No npm auth check         │
│  • No confirmation prompt    │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Skip OTP Retrieval           │
│  • No 1Password call         │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Simulate Actions             │
│  • Log version changes       │
│  • Skip actual file updates  │
│  • Run npm publish --dry-run │
│  • Skip git tagging          │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Show What Would Happen       │
│                              │
│ [yellow]DRY RUN: Would...   │
└──────────────────────────────┘
```

## Parallel vs Sequential Publishing

### Current: Sequential (Safer)

```
Plugin Package
    │
    ├─ Bump version
    ├─ Build
    ├─ Publish
    ▼
    [Wait for completion]

MCP Server Package
    │
    ├─ Bump version
    ├─ Build
    ├─ Publish
    ▼
    [Complete]
```

**Pros:**
- ✅ Safer (one failure doesn't affect other)
- ✅ Clear error reporting
- ✅ Can use same OTP for both

**Cons:**
- ⏱️ Takes longer (total time = sum of both)

### Future: Parallel (Faster)

```
Plugin Package          MCP Server Package
    │                        │
    ├─ Bump version          ├─ Bump version
    ├─ Build                 ├─ Build
    ├─ Publish               ├─ Publish
    ▼                        ▼
    [Both complete simultaneously]
```

**Pros:**
- ⚡ Faster (total time = max of both)

**Cons:**
- ⚠️ More complex error handling
- ⚠️ OTP might expire between publishes
- ⚠️ Partial success scenarios

## State Diagram

```
                     ┌─────────┐
                     │  IDLE   │
                     └────┬────┘
                          │
                          │ ./publish.py
                          ▼
                     ┌─────────┐
                     │ PARSING │
                     └────┬────┘
                          │
                          ▼
                   ┌──────────────┐
              ┌────┤  VALIDATING  ├────┐
              │    └──────────────┘    │
              │                        │
         [error]                  [success]
              │                        │
              ▼                        ▼
         ┌─────────┐          ┌───────────────┐
         │  ERROR  │          │  CONFIRMING   │
         └────┬────┘          └───────┬───────┘
              │                       │
              │                  [confirmed]
              │                       │
              │                       ▼
              │              ┌─────────────────┐
              │              │  PROCESSING     │
              │              │                 │
              │              │  ├─ Version     │
              │              │  ├─ Build       │
              │              │  └─ Publish     │
              │              └────────┬────────┘
              │                       │
              │                  [success]
              │                       │
              │                       ▼
              │              ┌─────────────────┐
              │              │  COMPLETED      │
              │              └─────────────────┘
              │
              ▼
         ┌──────────┐
         │  EXIT(1) │
         └──────────┘
```

## Command Variations

### All Possible Command Combinations

```bash
# Basic commands
./publish.py plugin
./publish.py mcp
./publish.py all

# With version bumping
./publish.py plugin --bump patch
./publish.py plugin --bump minor
./publish.py plugin --bump major

# With flags
./publish.py plugin --dry-run
./publish.py plugin --skip-build
./publish.py plugin --bump patch --dry-run
./publish.py plugin --bump patch --skip-build
./publish.py plugin --bump patch --dry-run --skip-build

# Short flags
./publish.py plugin -b patch
./publish.py plugin -b patch -d
./publish.py plugin -b patch -s
./publish.py plugin -b patch -d -s

# All packages
./publish.py all -b minor -d
```

## Integration Points

### External Tools

```
┌──────────────────────────────────────┐
│         publish.py                   │
│                                      │
│  Integrates with:                    │
│                                      │
│  ┌────────────┐  ┌────────────┐     │
│  │    git     │  │    npm     │     │
│  │            │  │            │     │
│  │ • status   │  │ • whoami   │     │
│  │ • tag      │  │ • publish  │     │
│  └────────────┘  └────────────┘     │
│                                      │
│  ┌────────────┐  ┌────────────┐     │
│  │ 1Password  │  │ filesystem │     │
│  │            │  │            │     │
│  │ • op CLI   │  │ • JSON R/W │     │
│  │ • OTP      │  │ • Path ops │     │
│  └────────────┘  └────────────┘     │
└──────────────────────────────────────┘
```

## Rollback Strategy

If publish fails midway (only for `all` command):

1. **Plugin published, MCP failed:**
   ```bash
   # Option 1: Manually unpublish plugin (within 72hrs)
   npm unpublish tauri-plugin-mcp@0.1.1

   # Option 2: Fix MCP issue and publish it separately
   ./publish.py mcp --bump patch
   ```

2. **Version bumped but publish failed:**
   ```bash
   # Revert package.json changes
   git restore package.json mcp-server-ts/package.json

   # Delete git tag
   git tag -d v0.1.1
   ```

3. **OTP expired during publish:**
   ```bash
   # Just run again (new OTP will be fetched)
   ./publish.py mcp --skip-build
   ```
