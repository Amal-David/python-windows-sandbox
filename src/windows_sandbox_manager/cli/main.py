"""
Main CLI entry point with rich interface.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config.models import SandboxConfig
from ..core.manager import SandboxManager
from ..core.sandbox import SandboxState
from ..exceptions import SandboxError
from ..utils.windows import WindowsUtils

console = Console()


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.pass_context
def cli(ctx, version):
    """Windows Sandbox Manager - Modern sandbox management for Windows."""
    if version:
        from .. import __version__

        console.print(f"Windows Sandbox Manager v{__version__}")
        return

    if ctx.invoked_subcommand is None:
        console.print(
            Panel.fit(
                "Windows Sandbox Manager\n\n"
                "A modern, secure Python library for Windows Sandbox management.\n"
                "Use --help to see available commands.",
                title="Welcome",
                style="blue",
            )
        )


@cli.command()
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
@click.option("--name", help="Override sandbox name from config")
def create(config_file: Path, name: Optional[str]):
    """Create and start a new sandbox from configuration file."""
    asyncio.run(_create_sandbox(config_file, name))


@cli.command()
@click.argument("sandbox_id", required=False)
@click.option("--name", help="Sandbox name to shutdown")
@click.option("--all", "shutdown_all", is_flag=True, help="Shutdown all sandboxes")
@click.option("--timeout", default=30, help="Shutdown timeout in seconds")
def shutdown(sandbox_id: Optional[str], name: Optional[str], shutdown_all: bool, timeout: int):
    """Shutdown sandbox(es)."""
    asyncio.run(_shutdown_sandbox(sandbox_id, name, shutdown_all, timeout))


@cli.command()
@click.option(
    "--state",
    type=click.Choice(["pending", "creating", "running", "stopping", "stopped", "failed"]),
    help="Filter by state",
)
def list(state: Optional[str]):
    """List all sandboxes."""
    asyncio.run(_list_sandboxes(state))


@cli.command()
@click.argument("sandbox_id")
@click.argument("command")
@click.option("--timeout", default=300, help="Command timeout in seconds")
def exec(sandbox_id: str, command: str, timeout: int):
    """Execute command in sandbox."""
    asyncio.run(_exec_command(sandbox_id, command, timeout))


@cli.command()
@click.argument("sandbox_id", required=False)
@click.option("--all", "monitor_all", is_flag=True, help="Monitor all sandboxes")
@click.option("--interval", default=5, help="Refresh interval in seconds")
def monitor(sandbox_id: Optional[str], monitor_all: bool, interval: int):
    """Monitor sandbox resource usage."""
    asyncio.run(_monitor_sandbox(sandbox_id, monitor_all, interval))


@cli.command()
def status():
    """Show system status and capabilities."""
    _show_status()


async def _create_sandbox(config_file: Path, name_override: Optional[str]):
    """Create sandbox implementation."""
    try:
        # Load configuration
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("Loading configuration...", total=None)

            config = SandboxConfig.from_file(config_file)

            if name_override:
                config.name = name_override

            progress.update(task, description="Creating sandbox manager...")
            manager = SandboxManager()

            progress.update(task, description=f"Creating sandbox '{config.name}'...")
            sandbox = await manager.create_sandbox(config)

            progress.update(task, description="Sandbox created successfully!")

        console.print(
            f"[green]SUCCESS[/green] Sandbox '{sandbox.config.name}' created successfully!"
        )
        console.print(f"   ID: {sandbox.id}")
        console.print(f"   State: {sandbox.state.value}")
        console.print(f"   Memory: {sandbox.config.memory_mb}MB")
        console.print(f"   CPU Cores: {sandbox.config.cpu_cores}")

    except SandboxError as e:
        console.print(f"[red]ERROR[/red] Error creating sandbox: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]ERROR[/red] Unexpected error: {e}")
        sys.exit(1)


async def _shutdown_sandbox(
    sandbox_id: Optional[str], name: Optional[str], shutdown_all: bool, timeout: int
):
    """Shutdown sandbox implementation."""
    try:
        manager = SandboxManager()

        if shutdown_all:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Shutting down all sandboxes...", total=None)
                await manager.shutdown_all(timeout)
            console.print("[green]SUCCESS[/green] All sandboxes shut down successfully!")

        elif sandbox_id:
            await manager.shutdown_sandbox(sandbox_id, timeout)
            console.print(f"[green]SUCCESS[/green] Sandbox {sandbox_id} shut down successfully!")

        elif name:
            sandbox = manager.get_sandbox_by_name(name)
            if not sandbox:
                console.print(f"[red]ERROR[/red] Sandbox '{name}' not found")
                sys.exit(1)
            await manager.shutdown_sandbox(sandbox.id, timeout)
            console.print(f"[green]SUCCESS[/green] Sandbox '{name}' shut down successfully!")

        else:
            console.print("[red]ERROR[/red] Must specify sandbox ID, name, or --all")
            sys.exit(1)

    except SandboxError as e:
        console.print(f"[red]ERROR[/red] Error shutting down sandbox: {e}")
        sys.exit(1)


async def _list_sandboxes(state_filter: Optional[str]):
    """List sandboxes implementation."""
    try:
        manager = SandboxManager()

        filter_state = None
        if state_filter:
            filter_state = SandboxState(state_filter)

        sandboxes = manager.list_sandboxes(filter_state)

        if not sandboxes:
            console.print("No sandboxes found.")
            return

        table = Table(title="Sandboxes")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("State", style="yellow")
        table.add_column("Memory", justify="right")
        table.add_column("CPU", justify="right")
        table.add_column("Uptime", justify="right")

        for sandbox in sandboxes:
            uptime_str = f"{sandbox.uptime:.0f}s"
            state_style = {
                SandboxState.RUNNING: "green",
                SandboxState.STOPPED: "red",
                SandboxState.FAILED: "red bold",
                SandboxState.CREATING: "yellow",
                SandboxState.STOPPING: "yellow",
                SandboxState.PENDING: "blue",
            }.get(sandbox.state, "white")

            table.add_row(
                sandbox.id[:8] + "...",
                sandbox.config.name,
                f"[{state_style}]{sandbox.state.value}[/{state_style}]",
                f"{sandbox.config.memory_mb}MB",
                f"{sandbox.config.cpu_cores}",
                uptime_str,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]ERROR[/red] Error listing sandboxes: {e}")
        sys.exit(1)


async def _exec_command(sandbox_id: str, command: str, timeout: int):
    """Execute command implementation."""
    try:
        manager = SandboxManager()
        sandbox = manager.get_sandbox(sandbox_id)

        if not sandbox:
            console.print(f"[red]ERROR[/red] Sandbox '{sandbox_id}' not found")
            sys.exit(1)

        if not sandbox.is_running:
            console.print(f"[red]ERROR[/red] Sandbox '{sandbox_id}' is not running")
            sys.exit(1)

        console.print(f"Executing: {command}")
        result = await sandbox.execute(command, timeout)

        if result.stdout:
            console.print("STDOUT:", style="green")
            console.print(result.stdout)

        if result.stderr:
            console.print("STDERR:", style="red")
            console.print(result.stderr)

        console.print(f"Exit code: {result.returncode}")
        console.print(f"Execution time: {result.execution_time:.2f}s")

        if not result.success:
            sys.exit(result.returncode)

    except SandboxError as e:
        console.print(f"[red]ERROR[/red] Error executing command: {e}")
        sys.exit(1)


async def _monitor_sandbox(sandbox_id: Optional[str], monitor_all: bool, interval: int):
    """Monitor sandbox implementation."""
    try:
        manager = SandboxManager()
        
        if monitor_all:
            sandboxes = manager.list_sandboxes(SandboxState.RUNNING)
            if not sandboxes:
                console.print("No running sandboxes to monitor.")
                return
        else:
            if not sandbox_id:
                console.print("[red]ERROR[/red] Must specify sandbox ID or use --all")
                sys.exit(1)
                
            sandbox = manager.get_sandbox(sandbox_id)
            if not sandbox:
                console.print(f"[red]ERROR[/red] Sandbox '{sandbox_id}' not found")
                sys.exit(1)
                
            if not sandbox.is_running:
                console.print(f"[red]ERROR[/red] Sandbox '{sandbox_id}' is not running")
                sys.exit(1)
                
            sandboxes = [sandbox]
        
        console.print(f"Monitoring {len(sandboxes)} sandbox(es). Press Ctrl+C to stop.")
        console.print()
        
        try:
            while True:
                # Create monitoring table
                table = Table(title=f"Resource Monitor (Interval: {interval}s)")
                table.add_column("Sandbox", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Memory", justify="right", style="yellow")
                table.add_column("CPU", justify="right", style="blue")
                table.add_column("Disk", justify="right", style="magenta")
                table.add_column("Uptime", justify="right", style="white")
                
                for sandbox in sandboxes:
                    if sandbox._resource_monitor:
                        stats = await sandbox._resource_monitor.get_stats()
                        table.add_row(
                            sandbox.id[:8] + "...",
                            sandbox.config.name,
                            f"{stats.memory_mb}MB",
                            f"{stats.cpu_percent:.1f}%",
                            f"{stats.disk_mb}MB",
                            f"{sandbox.uptime:.0f}s"
                        )
                    else:
                        table.add_row(
                            sandbox.id[:8] + "...",
                            sandbox.config.name,
                            "N/A",
                            "N/A",
                            "N/A",
                            f"{sandbox.uptime:.0f}s"
                        )
                
                # Clear screen and show table
                console.clear()
                console.print(table)
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped by user[/yellow]")
            
    except SandboxError as e:
        console.print(f"[red]ERROR[/red] Error monitoring sandbox: {e}")
        sys.exit(1)


def _show_status():
    """Show system status."""
    system_info = WindowsUtils.get_system_info()

    table = Table(title="System Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for key, value in system_info.items():
        formatted_key = key.replace("_", " ").title()
        table.add_row(formatted_key, str(value))

    console.print(table)

    # Check sandbox support
    if WindowsUtils.is_windows():
        if WindowsUtils.check_sandbox_support():
            console.print("[green]SUCCESS[/green] Windows Sandbox is supported and available")
        else:
            console.print("[red]ERROR[/red] Windows Sandbox is not available")
            console.print("   Make sure Windows Sandbox feature is enabled")
    else:
        console.print("[red]ERROR[/red] Not running on Windows")


if __name__ == "__main__":
    cli()
