"""
CLI Module for the Calculator Backend.
Provides an interactive Rich-based interface for mathematical evaluation.
"""

import sys

from colorama import init
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Backend imports
from calculator.calculator import evaluate
from calculator.history import clear_history
from calculator.history import get_history


def _is_critical_error(error_msg: str) -> bool:
    """
    Return True if the error message indicates a critical system/math error.
    Extracted for unit testing purposes.
    """
    critical_keywords = ("division by zero", "too large", "unexpected system")
    msg_lower = error_msg.lower()
    return any(k in msg_lower for k in critical_keywords)


def print_welcome(console: Console) -> None:
    """Displays a styled welcome panel."""
    welcome_text = Text(
        "A professional calculator built from scratch.", style="italic white"
    )
    panel = Panel(
        welcome_text,
        title="[bold cyan]Calculator v1.0.0[/bold cyan]",
        subtitle="Ready for input",
        border_style="cyan",
    )
    console.print(panel)


def print_help(console: Console) -> None:
    """Displays a table of supported operators and commands."""
    table = Table(title="Available Operations", border_style="blue")
    table.add_column("Operator", style="cyan")
    table.add_column("Symbol", justify="center")
    table.add_column("Example", style="green")
    table.add_column("Notes")

    table.add_row("Addition", "+", "2 + 2", "Standard sum")
    table.add_row("Subtraction", "-", "10 - 5", "Standard difference")
    table.add_row("Multiplication", "*", "3 * 4", "Standard product")
    table.add_row("Division", "/", "8 / 2", "Float division")
    table.add_row("Power", "^", "2 ^ 3", "Exponentiation")
    table.add_row("Square Root", "√", "√(16)", "Square root function")

    console.print(table)

    cmd_table = Table(title="Special Commands", show_header=False, border_style="dim")
    cmd_table.add_row("exit / quit", "Exit the application")
    cmd_table.add_row("history", "Show recent calculations")
    cmd_table.add_row("clear", "Wipe calculation history")
    cmd_table.add_row("help / ?", "Show this help menu")
    console.print(cmd_table)


def print_history(console: Console) -> None:
    """Displays calculation history in a table."""
    history = get_history()
    if not history:
        console.print("[yellow]History is currently empty.[/yellow]", style="italic")
        return

    table = Table(title="Calculation History", border_style="magenta")
    table.add_column("Expression", style="cyan")
    table.add_column("Result", style="green")
    table.add_column("Time", style="dim")

    for entry in history:
        # Accessing NamedTuple attributes: .expression, .result, .timestamp
        table.add_row(entry.expression, str(entry.result), entry.timestamp)

    console.print(table)


def print_error(console: Console, message: str, critical: bool = False) -> None:
    """Prints formatted error messages."""
    if critical:
        console.print(f"[bold red]🚨 Critical Error:[/bold red] {message}")
    else:
        console.print(f"[bold yellow]❗ Error:[/bold yellow] {message}")


def main() -> None:
    """Main entry point for the CLI."""
    init(autoreset=True)
    console = Console()

    # Handle Piped Input (Non-Interactive)
    if not sys.stdin.isatty():
        for line in sys.stdin:
            expr = line.strip()
            if not expr:
                continue
            if len(expr) > 255:
                print("Error: Input exceeds 255 character limit.")
                continue
            res = evaluate(expr)
            print(res.value if res.success else f"Error: {res.error}")
        sys.exit(0)

    # Interactive Mode
    print_welcome(console)

    try:
        while True:
            try:
                user_input = console.input("[bold blue]calc[/bold blue] > ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            cmd = user_input.lower()
            if cmd in ("exit", "quit"):
                console.print(Panel("Goodbye!", border_style="cyan"))
                break
            elif cmd in ("help", "?"):
                print_help(console)
            elif cmd == "history":
                print_history(console)
            elif cmd == "clear":
                clear_history()
                console.print("[green]History cleared successfully.[/green]")
            elif len(user_input) > 255:
                print_error(console, "Input exceeds 255 character limit.")
            else:
                res = evaluate(user_input)
                if res.success:
                    console.print(f"[bold green]{res.value}[/bold green]")
                else:
                    is_critical = _is_critical_error(str(res.error))
                    print_error(console, str(res.error), critical=is_critical)

    except KeyboardInterrupt:
        console.print("\n[cyan]Session interrupted. Goodbye![/cyan]")
        sys.exit(0)


if __name__ == "__main__":
    main()
