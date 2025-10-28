#!/usr/bin/env python3
"""
Production build script for Tauri MCP Server project.

This script manages the build process for a dual-artifact project:
- Tauri plugin (Rust/Cargo) -> Builds Rust library
- MCP server (TypeScript/Node.js) -> Builds TypeScript to JavaScript

Usage:
    python build.py plugin [OPTIONS]
    python build.py mcp [OPTIONS]
    python build.py all [OPTIONS]

Examples:
    python build.py all --clean --verbose
    python build.py plugin --target x86_64-unknown-linux-gnu
    python build.py mcp --clean
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Initialize Rich console for beautiful output
console = Console()
app = typer.Typer(
    name="build",
    help="Build system for Tauri MCP Server project",
    add_completion=False,
)

# Project paths
PROJECT_ROOT = Path(__file__).parent.absolute()
MCP_SERVER_DIR = PROJECT_ROOT / "mcp-server-ts"
DIST_JS_DIR = PROJECT_ROOT / "dist-js"
TARGET_DIR = PROJECT_ROOT / "target"
MCP_BUILD_DIR = MCP_SERVER_DIR / "build"


class BuildTarget(str, Enum):
    """Supported build targets."""

    PLUGIN = "plugin"
    MCP = "mcp"
    ALL = "all"


class BuildError(Exception):
    """Custom exception for build errors."""

    pass


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in the system PATH.

    Args:
        command: Command name to check

    Returns:
        True if command exists, False otherwise
    """
    return shutil.which(command) is not None


def validate_tools(targets: list[BuildTarget]) -> None:
    """
    Validate that required build tools are installed.

    Args:
        targets: List of build targets to validate tools for

    Raises:
        BuildError: If required tools are missing
    """
    required_tools: dict[str, list[BuildTarget]] = {
        "cargo": [BuildTarget.PLUGIN, BuildTarget.ALL],
        "rustc": [BuildTarget.PLUGIN, BuildTarget.ALL],
        "bun": [BuildTarget.MCP, BuildTarget.ALL],
    }

    missing_tools: list[str] = []

    for tool, tool_targets in required_tools.items():
        if any(target in tool_targets for target in targets):
            if not check_command_exists(tool):
                missing_tools.append(tool)

    if missing_tools:
        console.print(
            Panel(
                f"[red]Missing required tools:[/red]\n"
                + "\n".join(f"  • {tool}" for tool in missing_tools),
                title="Build Prerequisites Failed",
                border_style="red",
            )
        )
        raise BuildError(f"Missing required tools: {', '.join(missing_tools)}")


def run_command(
    command: list[str],
    cwd: Path | None = None,
    verbose: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """
    Run a shell command with error handling.

    Args:
        command: Command and arguments to run
        cwd: Working directory for command execution
        verbose: If True, show command output in real-time
        env: Optional environment variables

    Returns:
        CompletedProcess instance

    Raises:
        BuildError: If command fails
    """
    cmd_str = " ".join(command)

    if verbose:
        console.print(f"[dim]Running: {cmd_str}[/dim]")

    try:
        if verbose:
            # Stream output in real-time
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
            )

            if process.stdout:
                for line in process.stdout:
                    console.print(f"  {line.rstrip()}", style="dim")

            return_code = process.wait()

            if return_code != 0:
                raise BuildError(f"Command failed with exit code {return_code}")

            return subprocess.CompletedProcess(
                args=command,
                returncode=return_code,
                stdout="",
                stderr="",
            )
        else:
            # Capture output silently
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
            return result

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Command failed:[/red] {cmd_str}")
        if e.stdout:
            console.print("[red]STDOUT:[/red]")
            console.print(e.stdout)
        if e.stderr:
            console.print("[red]STDERR:[/red]")
            console.print(e.stderr)
        raise BuildError(f"Command failed: {cmd_str}") from e
    except FileNotFoundError as e:
        raise BuildError(f"Command not found: {command[0]}") from e


def clean_directory(directory: Path, verbose: bool = False) -> None:
    """
    Remove a directory and all its contents.

    Args:
        directory: Directory path to remove
        verbose: If True, show what's being cleaned
    """
    if directory.exists():
        if verbose:
            console.print(f"[yellow]Cleaning:[/yellow] {directory}")
        shutil.rmtree(directory)
        if verbose:
            console.print(f"[green]Cleaned:[/green] {directory}")


def build_plugin(
    clean: bool = False,
    verbose: bool = False,
    release: bool = True,
    target: str | None = None,
) -> None:
    """
    Build the Rust Tauri plugin.

    Args:
        clean: Clean build artifacts before building
        verbose: Show detailed build output
        release: Build in release mode
        target: Optional Rust target triple
    """
    console.print("\n[bold cyan]Building Tauri Plugin (Rust)[/bold cyan]\n")

    # Clean if requested
    if clean:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Cleaning plugin artifacts...", total=None)
            clean_directory(TARGET_DIR, verbose)
            clean_directory(DIST_JS_DIR, verbose)
            progress.update(task, completed=True)
            console.print("[green]✓[/green] Plugin artifacts cleaned\n")

    # Build Rust plugin
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Building Rust plugin...", total=None)

        command = ["cargo", "build"]

        if release:
            command.append("--release")

        if target:
            command.extend(["--target", target])

        if verbose:
            console.print(f"[dim]Command: {' '.join(command)}[/dim]\n")

        run_command(command, cwd=PROJECT_ROOT, verbose=verbose)

        progress.update(task, completed=True)

    # Build JavaScript bindings
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Building JavaScript bindings...", total=None)

        # Check which package manager to use
        if check_command_exists("bun"):
            run_command(["bun", "run", "build"], cwd=PROJECT_ROOT, verbose=verbose)
        elif check_command_exists("npm"):
            run_command(["npm", "run", "build"], cwd=PROJECT_ROOT, verbose=verbose)
        else:
            raise BuildError("Neither bun nor npm found for building JS bindings")

        progress.update(task, completed=True)

    console.print("[green]✓[/green] Plugin build complete\n")


def build_mcp(clean: bool = False, verbose: bool = False) -> None:
    """
    Build the TypeScript MCP server.

    Args:
        clean: Clean build artifacts before building
        verbose: Show detailed build output
    """
    console.print("\n[bold cyan]Building MCP Server (TypeScript)[/bold cyan]\n")

    # Validate MCP server directory exists
    if not MCP_SERVER_DIR.exists():
        raise BuildError(
            f"MCP server directory not found: {MCP_SERVER_DIR}"
        )

    # Clean if requested
    if clean:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Cleaning MCP artifacts...", total=None)
            clean_directory(MCP_BUILD_DIR, verbose)
            progress.update(task, completed=True)
            console.print("[green]✓[/green] MCP artifacts cleaned\n")

    # Build TypeScript
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Compiling TypeScript...", total=None)

        # Check which package manager to use
        if check_command_exists("bun"):
            run_command(
                ["bun", "run", "build"],
                cwd=MCP_SERVER_DIR,
                verbose=verbose,
            )
        elif check_command_exists("npm"):
            run_command(
                ["npm", "run", "build"],
                cwd=MCP_SERVER_DIR,
                verbose=verbose,
            )
        else:
            raise BuildError("Neither bun nor npm found for building MCP server")

        progress.update(task, completed=True)

    console.print("[green]✓[/green] MCP server build complete\n")


def show_build_summary(
    targets: list[BuildTarget],
    clean: bool,
    verbose: bool,
    release: bool,
    target: str | None,
) -> None:
    """
    Display a summary of the build configuration.

    Args:
        targets: Build targets that will be built
        clean: Whether cleaning is enabled
        verbose: Whether verbose mode is enabled
        release: Whether release mode is enabled
        target: Target triple if specified
    """
    table = Table(title="Build Configuration", show_header=False, box=None)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Targets", ", ".join(t.value for t in targets))
    table.add_row("Clean", "Yes" if clean else "No")
    table.add_row("Verbose", "Yes" if verbose else "No")
    table.add_row("Release Mode", "Yes" if release else "No")

    if target:
        table.add_row("Rust Target", target)

    console.print(table)
    console.print()


@app.command()
def plugin(
    clean: Annotated[
        bool,
        typer.Option("--clean", "-c", help="Clean build artifacts before building"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed build output"),
    ] = False,
    release: Annotated[
        bool,
        typer.Option("--release", "-r", help="Build in release mode"),
    ] = True,
    target: Annotated[
        Optional[str],
        typer.Option("--target", "-t", help="Rust target triple (e.g., x86_64-unknown-linux-gnu)"),
    ] = None,
) -> None:
    """Build the Rust Tauri plugin."""
    try:
        console.print(
            Panel(
                "[bold]Tauri MCP Server - Plugin Build[/bold]",
                border_style="cyan",
            )
        )

        show_build_summary([BuildTarget.PLUGIN], clean, verbose, release, target)
        validate_tools([BuildTarget.PLUGIN])
        build_plugin(clean=clean, verbose=verbose, release=release, target=target)

        console.print(
            Panel(
                "[bold green]Plugin build successful! ✓[/bold green]",
                border_style="green",
            )
        )
        sys.exit(0)

    except BuildError as e:
        console.print(
            Panel(
                f"[bold red]Build failed:[/bold red]\n{e}",
                border_style="red",
            )
        )
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Build interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Unexpected error:[/bold red]\n{e}",
                border_style="red",
            )
        )
        if verbose:
            console.print_exception()
        sys.exit(1)


@app.command()
def mcp(
    clean: Annotated[
        bool,
        typer.Option("--clean", "-c", help="Clean build artifacts before building"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed build output"),
    ] = False,
) -> None:
    """Build the TypeScript MCP server."""
    try:
        console.print(
            Panel(
                "[bold]Tauri MCP Server - MCP Build[/bold]",
                border_style="cyan",
            )
        )

        show_build_summary([BuildTarget.MCP], clean, verbose, False, None)
        validate_tools([BuildTarget.MCP])
        build_mcp(clean=clean, verbose=verbose)

        console.print(
            Panel(
                "[bold green]MCP server build successful! ✓[/bold green]",
                border_style="green",
            )
        )
        sys.exit(0)

    except BuildError as e:
        console.print(
            Panel(
                f"[bold red]Build failed:[/bold red]\n{e}",
                border_style="red",
            )
        )
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Build interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Unexpected error:[/bold red]\n{e}",
                border_style="red",
            )
        )
        if verbose:
            console.print_exception()
        sys.exit(1)


@app.command()
def all(
    clean: Annotated[
        bool,
        typer.Option("--clean", "-c", help="Clean build artifacts before building"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed build output"),
    ] = False,
    release: Annotated[
        bool,
        typer.Option("--release", "-r", help="Build plugin in release mode"),
    ] = True,
    target: Annotated[
        Optional[str],
        typer.Option("--target", "-t", help="Rust target triple (e.g., x86_64-unknown-linux-gnu)"),
    ] = None,
) -> None:
    """Build both the plugin and MCP server."""
    try:
        console.print(
            Panel(
                "[bold]Tauri MCP Server - Full Build[/bold]",
                border_style="cyan",
            )
        )

        show_build_summary([BuildTarget.ALL], clean, verbose, release, target)
        validate_tools([BuildTarget.ALL])

        # Build plugin first
        build_plugin(clean=clean, verbose=verbose, release=release, target=target)

        # Build MCP server
        build_mcp(clean=clean, verbose=verbose)

        console.print(
            Panel(
                "[bold green]All builds successful! ✓[/bold green]",
                border_style="green",
            )
        )
        sys.exit(0)

    except BuildError as e:
        console.print(
            Panel(
                f"[bold red]Build failed:[/bold red]\n{e}",
                border_style="red",
            )
        )
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Build interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Unexpected error:[/bold red]\n{e}",
                border_style="red",
            )
        )
        if verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    app()
