#!/usr/bin/env python3
"""
Process Monitor CLI - A terminal-based process management tool for Termux
"""

import os
import sys
import subprocess
import signal
from typing import List, Dict, Optional
from datetime import datetime
import re

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    from rich.prompt import Prompt, Confirm
    from rich.progress import track
except ImportError:
    print("❌ Error: Required packages not installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

console = Console()


class ProcessMonitor:
    """Main Process Monitor class"""

    def __init__(self):
        self.processes = []
        self.refresh_data()

    def refresh_data(self):
        """Refresh process list"""
        try:
            # Get process list using ps command
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.processes = self._parse_processes(result.stdout)
        except Exception as e:
            console.print(f"[red]Error refreshing processes: {e}[/red]")
            self.processes = []

    def _parse_processes(self, output: str) -> List[Dict]:
        """Parse ps output into structured data"""
        lines = output.strip().split('\n')
        processes = []
        
        for line in lines[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 11:
                processes.append({
                    'user': parts[0],
                    'pid': parts[1],
                    'cpu': parts[2],
                    'mem': parts[3],
                    'vsz': parts[4],
                    'rss': parts[5],
                    'tty': parts[6],
                    'stat': parts[7],
                    'start': parts[8],
                    'time': parts[9],
                    'command': ' '.join(parts[10:])
                })
        
        return processes

    def display_all(self):
        """Display all processes in a table"""
        if not self.processes:
            console.print("[yellow]No processes found[/yellow]")
            return

        table = Table(title="[bold cyan]Process Monitor[/bold cyan]", box=box.ROUNDED)
        table.add_column("PID", style="cyan", width=8)
        table.add_column("User", style="magenta", width=12)
        table.add_column("CPU %", style="yellow", width=8)
        table.add_column("Memory %", style="green", width=10)
        table.add_column("Command", style="white", width=40)

        for proc in sorted(self.processes, key=lambda x: float(x['cpu']), reverse=True)[:30]:
            table.add_row(
                proc['pid'],
                proc['user'][:12],
                proc['cpu'],
                proc['mem'],
                proc['command'][:40]
            )

        console.print(table)

    def search_process(self, keyword: str) -> List[Dict]:
        """Search for processes by name"""
        keyword_lower = keyword.lower()
        return [p for p in self.processes if keyword_lower in p['command'].lower()]

    def display_search_results(self, keyword: str):
        """Display search results"""
        results = self.search_process(keyword)
        
        if not results:
            console.print(f"[yellow]No processes found matching '{keyword}'[/yellow]")
            return

        table = Table(title=f"[bold cyan]Search Results: '{keyword}'[/bold cyan]", box=box.ROUNDED)
        table.add_column("PID", style="cyan", width=8)
        table.add_column("User", style="magenta", width=12)
        table.add_column("CPU %", style="yellow", width=8)
        table.add_column("Memory %", style="green", width=10)
        table.add_column("Command", style="white", width=40)

        for proc in results[:20]:
            table.add_row(
                proc['pid'],
                proc['user'][:12],
                proc['cpu'],
                proc['mem'],
                proc['command'][:40]
            )

        console.print(table)

    def get_process_details(self, pid: str) -> Optional[Dict]:
        """Get detailed information about a specific process"""
        for proc in self.processes:
            if proc['pid'] == pid:
                return proc
        return None

    def display_process_details(self, pid: str):
        """Display detailed process information"""
        proc = self.get_process_details(pid)
        
        if not proc:
            console.print(f"[red]Process {pid} not found[/red]")
            return

        panel_content = f"""
[cyan]PID:[/cyan]        {proc['pid']}
[cyan]User:[/cyan]       {proc['user']}
[cyan]CPU %:[/cyan]      {proc['cpu']}
[cyan]Memory %:[/cyan]   {proc['mem']}
[cyan]VSZ:[/cyan]        {proc['vsz']}
[cyan]RSS:[/cyan]        {proc['rss']}
[cyan]TTY:[/cyan]        {proc['tty']}
[cyan]STAT:[/cyan]       {proc['stat']}
[cyan]Start:[/cyan]      {proc['start']}
[cyan]Time:[/cyan]       {proc['time']}
[cyan]Command:[/cyan]    {proc['command']}
        """
        
        console.print(Panel(panel_content, title=f"Process Details", expand=False))

    def kill_process(self, pid: str, force: bool = False) -> bool:
        """Kill a process"""
        try:
            signal_type = signal.SIGKILL if force else signal.SIGTERM
            os.kill(int(pid), signal_type)
            console.print(f"[green]✓ Process {pid} terminated[/green]")
            return True
        except ProcessLookupError:
            console.print(f"[red]✗ Process {pid} not found[/red]")
            return False
        except PermissionError:
            console.print(f"[red]✗ Permission denied (may need sudo)[/red]")
            return False
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def show_top_processes(self, limit: int = 10):
        """Show top processes by CPU/Memory usage"""
        if not self.processes:
            console.print("[yellow]No processes found[/yellow]")
            return

        console.print("\n[bold]Top 10 Processes by CPU Usage:[/bold]")
        table = Table(box=box.ROUNDED)
        table.add_column("PID", style="cyan", width=8)
        table.add_column("User", style="magenta", width=12)
        table.add_column("CPU %", style="red", width=8)
        table.add_column("Command", style="white", width=40)

        for proc in sorted(self.processes, key=lambda x: float(x['cpu']), reverse=True)[:limit]:
            table.add_row(
                proc['pid'],
                proc['user'][:12],
                proc['cpu'],
                proc['command'][:40]
            )

        console.print(table)


def show_menu():
    """Display main menu"""
    console.clear()
    console.print("[bold cyan]╔══════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║   Process Monitor - Termux Edition   ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════╝[/bold cyan]\n")
    
    menu_options = [
        "[1] View all processes",
        "[2] Search for process",
        "[3] Process details",
        "[4] Top processes (by CPU)",
        "[5] Kill process",
        "[6] Kill process (force)",
        "[7] Refresh",
        "[0] Exit"
    ]
    
    for option in menu_options:
        console.print(option)
    console.print()


def main():
    """Main application loop"""
    monitor = ProcessMonitor()

    while True:
        show_menu()
        choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6", "7"])

        if choice == "0":
            console.print("[cyan]Goodbye! 👋[/cyan]")
            break

        elif choice == "1":
            monitor.refresh_data()
            monitor.display_all()
            input("\nPress Enter to continue...")

        elif choice == "2":
            keyword = Prompt.ask("Enter process name to search")
            monitor.search_process(keyword)
            monitor.display_search_results(keyword)
            input("\nPress Enter to continue...")

        elif choice == "3":
            pid = Prompt.ask("Enter PID")
            monitor.display_process_details(pid)
            input("\nPress Enter to continue...")

        elif choice == "4":
            monitor.refresh_data()
            monitor.show_top_processes()
            input("\nPress Enter to continue...")

        elif choice == "5":
            pid = Prompt.ask("Enter PID to kill")
            if Confirm.ask(f"Kill process {pid}?"):
                monitor.kill_process(pid, force=False)
                monitor.refresh_data()
            input("\nPress Enter to continue...")

        elif choice == "6":
            pid = Prompt.ask("Enter PID to force kill")
            if Confirm.ask(f"Force kill process {pid}? [warning]This may cause data loss[/warning]"):
                monitor.kill_process(pid, force=True)
                monitor.refresh_data()
            input("\nPress Enter to continue...")

        elif choice == "7":
            monitor.refresh_data()
            console.print("[green]✓ Process list refreshed[/green]")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)
