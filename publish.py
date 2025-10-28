#!/usr/bin/env python3
"""
Production-ready publish script for Tauri MCP project.

This script handles publishing both the Tauri plugin (root package) and the MCP server
(mcp-server-ts package) to npm registry with version management, 1Password OTP integration,
and comprehensive safety checks.

Usage:
    python publish.py plugin [--bump patch|minor|major] [--dry-run] [--skip-build]
    python publish.py mcp [--bump patch|minor|major] [--dry-run] [--skip-build]
    python publish.py all [--bump patch|minor|major] [--dry-run] [--skip-build]
"""

import json
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

# Initialize Rich console for beautiful output
console = Console()

# Project paths
PROJECT_ROOT = Path(__file__).parent.resolve()
PLUGIN_PACKAGE_JSON = PROJECT_ROOT / "package.json"
MCP_PACKAGE_JSON = PROJECT_ROOT / "mcp-server-ts" / "package.json"

# 1Password configuration
ONEPASSWORD_VAULT = "DeLoSecrets"
ONEPASSWORD_ITEM = "npmjs"

# Initialize Typer app
app = typer.Typer(
    name="publish",
    help="Publish Tauri MCP project packages to npm registry",
    add_completion=False,
)


class BumpType(str, Enum):
    """Semantic version bump types."""

    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


class PublishTarget(str, Enum):
    """Available publish targets."""

    PLUGIN = "plugin"
    MCP = "mcp"
    ALL = "all"


class PackageInfo:
    """Package information and metadata."""

    def __init__(self, name: str, path: Path, package_json_path: Path):
        self.name = name
        self.path = path
        self.package_json_path = package_json_path
        self._data: dict = {}
        self._load_package_json()

    def _load_package_json(self) -> None:
        """Load package.json data."""
        try:
            with open(self.package_json_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            console.print(
                f"[red]Error: package.json not found at {self.package_json_path}[/red]"
            )
            raise typer.Exit(1)
        except json.JSONDecodeError as e:
            console.print(
                f"[red]Error: Invalid JSON in {self.package_json_path}: {e}[/red]"
            )
            raise typer.Exit(1)

    @property
    def npm_name(self) -> str:
        """Get the npm package name."""
        return self._data.get("name", "unknown")

    @property
    def version(self) -> str:
        """Get the current package version."""
        return self._data.get("version", "0.0.0")

    def bump_version(self, bump_type: BumpType) -> str:
        """
        Bump the version according to semver rules.

        Args:
            bump_type: Type of version bump (patch, minor, major)

        Returns:
            The new version string
        """
        major, minor, patch = map(int, self.version.split("."))

        if bump_type == BumpType.MAJOR:
            major += 1
            minor = 0
            patch = 0
        elif bump_type == BumpType.MINOR:
            minor += 1
            patch = 0
        elif bump_type == BumpType.PATCH:
            patch += 1

        return f"{major}.{minor}.{patch}"

    def update_version(self, new_version: str, dry_run: bool = False) -> None:
        """
        Update the package.json with the new version.

        Args:
            new_version: The new version string
            dry_run: If True, only show what would be changed
        """
        if dry_run:
            console.print(
                f"[yellow]DRY RUN: Would update {self.package_json_path} "
                f"version to {new_version}[/yellow]"
            )
            return

        self._data["version"] = new_version

        with open(self.package_json_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline

        console.print(
            f"[green]Updated {self.package_json_path} to version {new_version}[/green]"
        )


def run_command(
    cmd: list[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess:
    """
    Run a shell command with error handling.

    Args:
        cmd: Command and arguments as a list
        cwd: Working directory for the command
        check: If True, raise exception on non-zero exit
        capture_output: If True, capture stdout and stderr

    Returns:
        CompletedProcess instance

    Raises:
        subprocess.CalledProcessError: If command fails and check=True
    """
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Command failed: {' '.join(cmd)}[/red]")
        if capture_output and e.stderr:
            console.print(f"[red]Error: {e.stderr}[/red]")
        raise


def check_git_clean() -> bool:
    """
    Check if the git working directory is clean.

    Returns:
        True if working directory is clean, False otherwise
    """
    try:
        result = run_command(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT,
            capture_output=True,
        )
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError:
        console.print("[yellow]Warning: Could not check git status[/yellow]")
        return True  # Continue anyway


def check_npm_credentials() -> bool:
    """
    Check if npm credentials are configured.

    Returns:
        True if npm is logged in, False otherwise
    """
    try:
        result = run_command(
            ["npm", "whoami"],
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            username = result.stdout.strip()
            console.print(f"[green]Logged in to npm as: {username}[/green]")
            return True
        else:
            console.print(
                "[red]Not logged in to npm. Run 'npm login' first.[/red]"
            )
            return False
    except FileNotFoundError:
        console.print("[red]Error: npm command not found[/red]")
        return False


def get_otp_from_1password() -> Optional[str]:
    """
    Fetch npm OTP from 1Password using the `op` CLI.

    Returns:
        OTP code if successful, None otherwise
    """
    try:
        result = run_command(
            [
                "op",
                "item",
                "get",
                ONEPASSWORD_ITEM,
                "--vault",
                ONEPASSWORD_VAULT,
                "--fields",
                "otp",
            ],
            capture_output=True,
            check=False,
        )

        if result.returncode == 0:
            otp = result.stdout.strip()
            console.print("[green]Retrieved OTP from 1Password[/green]")
            return otp
        else:
            console.print(
                "[yellow]Could not retrieve OTP from 1Password[/yellow]"
            )
            return None

    except FileNotFoundError:
        console.print(
            "[yellow]1Password CLI (op) not found, skipping OTP[/yellow]"
        )
        return None


def create_git_tag(version: str, dry_run: bool = False) -> None:
    """
    Create a git tag for the version.

    Args:
        version: Version string for the tag
        dry_run: If True, only show what would be done
    """
    tag_name = f"v{version}"

    if dry_run:
        console.print(
            f"[yellow]DRY RUN: Would create git tag {tag_name}[/yellow]"
        )
        return

    try:
        run_command(
            ["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"],
            cwd=PROJECT_ROOT,
        )
        console.print(f"[green]Created git tag: {tag_name}[/green]")
    except subprocess.CalledProcessError:
        console.print(f"[yellow]Warning: Could not create git tag {tag_name}[/yellow]")


def build_package(pkg: PackageInfo, skip_build: bool = False, dry_run: bool = False) -> None:
    """
    Build the package before publishing.

    Args:
        pkg: Package information
        skip_build: If True, skip the build step
        dry_run: If True, only show what would be done
    """
    if skip_build:
        console.print(f"[yellow]Skipping build for {pkg.name}[/yellow]")
        return

    if dry_run:
        console.print(
            f"[yellow]DRY RUN: Would build {pkg.name}[/yellow]"
        )
        return

    with console.status(f"[bold blue]Building {pkg.name}..."):
        try:
            run_command(["npm", "run", "build"], cwd=pkg.path)
            console.print(f"[green]Successfully built {pkg.name}[/green]")
        except subprocess.CalledProcessError:
            console.print(f"[red]Build failed for {pkg.name}[/red]")
            raise typer.Exit(1)


def publish_package(
    pkg: PackageInfo,
    otp: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """
    Publish a package to npm.

    Args:
        pkg: Package information
        otp: One-time password for npm 2FA
        dry_run: If True, perform a dry run without actually publishing
    """
    cmd = ["npm", "publish"]

    if otp:
        cmd.extend(["--otp", otp])

    if dry_run:
        cmd.append("--dry-run")
        console.print(f"[yellow]DRY RUN: {' '.join(cmd)}[/yellow]")

    try:
        with console.status(f"[bold blue]Publishing {pkg.npm_name}..."):
            run_command(cmd, cwd=pkg.path)

        if dry_run:
            console.print(
                f"[green]Dry run successful for {pkg.npm_name}[/green]"
            )
        else:
            console.print(
                f"[green]Successfully published {pkg.npm_name}@{pkg.version}[/green]"
            )
    except subprocess.CalledProcessError:
        console.print(f"[red]Failed to publish {pkg.npm_name}[/red]")
        raise typer.Exit(1)


def display_publish_summary(
    packages: list[PackageInfo],
    bump_type: Optional[BumpType],
    dry_run: bool,
    skip_build: bool,
) -> None:
    """
    Display a summary table of what will be published.

    Args:
        packages: List of packages to publish
        bump_type: Type of version bump
        dry_run: Whether this is a dry run
        skip_build: Whether build is skipped
    """
    table = Table(title="Publish Summary", show_header=True, header_style="bold magenta")
    table.add_column("Package", style="cyan", width=30)
    table.add_column("Current Version", style="yellow")
    table.add_column("New Version", style="green")
    table.add_column("Path", style="blue")

    for pkg in packages:
        new_version = pkg.bump_version(bump_type) if bump_type else pkg.version
        table.add_row(
            pkg.npm_name,
            pkg.version,
            new_version if bump_type else "(no change)",
            str(pkg.path.relative_to(PROJECT_ROOT)),
        )

    console.print()
    console.print(table)
    console.print()

    # Display flags
    flags = []
    if dry_run:
        flags.append("[yellow]DRY RUN[/yellow]")
    if skip_build:
        flags.append("[yellow]SKIP BUILD[/yellow]")
    if bump_type:
        flags.append(f"[cyan]BUMP: {bump_type.value}[/cyan]")

    if flags:
        console.print(" | ".join(flags))
        console.print()


def get_packages(target: PublishTarget) -> list[PackageInfo]:
    """
    Get the list of packages to publish based on the target.

    Args:
        target: The publish target (plugin, mcp, or all)

    Returns:
        List of PackageInfo objects
    """
    packages = []

    if target in (PublishTarget.PLUGIN, PublishTarget.ALL):
        packages.append(
            PackageInfo(
                name="Tauri Plugin",
                path=PROJECT_ROOT,
                package_json_path=PLUGIN_PACKAGE_JSON,
            )
        )

    if target in (PublishTarget.MCP, PublishTarget.ALL):
        packages.append(
            PackageInfo(
                name="MCP Server",
                path=PROJECT_ROOT / "mcp-server-ts",
                package_json_path=MCP_PACKAGE_JSON,
            )
        )

    return packages


@app.command()
def plugin(
    bump: Annotated[
        Optional[BumpType],
        typer.Option("--bump", "-b", help="Version bump type (patch, minor, major)"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-d", help="Perform a dry run without publishing"),
    ] = False,
    skip_build: Annotated[
        bool,
        typer.Option("--skip-build", "-s", help="Skip the build step"),
    ] = False,
) -> None:
    """Publish the Tauri plugin package to npm."""
    console.print(Panel.fit("[bold cyan]Publishing Tauri Plugin[/bold cyan]"))
    _publish(PublishTarget.PLUGIN, bump, dry_run, skip_build)


@app.command()
def mcp(
    bump: Annotated[
        Optional[BumpType],
        typer.Option("--bump", "-b", help="Version bump type (patch, minor, major)"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-d", help="Perform a dry run without publishing"),
    ] = False,
    skip_build: Annotated[
        bool,
        typer.Option("--skip-build", "-s", help="Skip the build step"),
    ] = False,
) -> None:
    """Publish the MCP server package to npm."""
    console.print(Panel.fit("[bold cyan]Publishing MCP Server[/bold cyan]"))
    _publish(PublishTarget.MCP, bump, dry_run, skip_build)


@app.command()
def all(
    bump: Annotated[
        Optional[BumpType],
        typer.Option("--bump", "-b", help="Version bump type (patch, minor, major)"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-d", help="Perform a dry run without publishing"),
    ] = False,
    skip_build: Annotated[
        bool,
        typer.Option("--skip-build", "-s", help="Skip the build step"),
    ] = False,
) -> None:
    """Publish both plugin and MCP server packages to npm."""
    console.print(Panel.fit("[bold cyan]Publishing All Packages[/bold cyan]"))
    _publish(PublishTarget.ALL, bump, dry_run, skip_build)


def _publish(
    target: PublishTarget,
    bump: Optional[BumpType],
    dry_run: bool,
    skip_build: bool,
) -> None:
    """
    Internal publish implementation.

    Args:
        target: What to publish (plugin, mcp, or all)
        bump: Version bump type
        dry_run: Whether to perform a dry run
        skip_build: Whether to skip building
    """
    # Get packages to publish
    packages = get_packages(target)

    # Display summary
    display_publish_summary(packages, bump, dry_run, skip_build)

    # Safety checks
    if not dry_run:
        # Check git status
        if not check_git_clean():
            console.print(
                "[yellow]Warning: Git working directory is not clean[/yellow]"
            )
            if not Confirm.ask("Continue anyway?", default=False):
                console.print("[red]Publish cancelled[/red]")
                raise typer.Exit(0)

        # Check npm credentials
        if not check_npm_credentials():
            console.print("[red]Please log in to npm first with 'npm login'[/red]")
            raise typer.Exit(1)

        # Confirm publish
        if not Confirm.ask(
            "[bold yellow]Proceed with publish?[/bold yellow]", default=False
        ):
            console.print("[red]Publish cancelled[/red]")
            raise typer.Exit(0)

    # Get OTP if not dry run
    otp = None
    if not dry_run:
        otp = get_otp_from_1password()
        if not otp:
            console.print(
                "[yellow]Publishing without OTP. You may be prompted for it.[/yellow]"
            )

    # Process each package
    for pkg in packages:
        console.print()
        console.print(f"[bold]Processing {pkg.name}...[/bold]")

        # Bump version if requested
        if bump:
            new_version = pkg.bump_version(bump)
            pkg.update_version(new_version, dry_run)

            # Create git tag for the new version
            if not dry_run:
                create_git_tag(new_version, dry_run)

        # Build package
        build_package(pkg, skip_build, dry_run)

        # Publish package
        publish_package(pkg, otp, dry_run)

    # Success message
    console.print()
    if dry_run:
        console.print(
            Panel.fit(
                "[bold green]Dry run completed successfully![/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                "[bold green]All packages published successfully![/bold green]",
                border_style="green",
            )
        )
        console.print()
        console.print(
            "[cyan]Don't forget to push git tags:[/cyan] git push --tags"
        )


if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)
