"""Command-line interface for DevLab Guard policy enforcement and developer gates.

Module: devlab_guard.cli
"""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from devlab_guard.core.models import Severity
from devlab_guard.core.pipeline import run_pipeline

app = typer.Typer(
    name="guard",
    help="DevLab Guard — Autonomous AI Reviewer & AST Policy Enforcer",
    no_args_is_help=True,
)
console = Console()


@app.command(name="check")
def check(
    path: str = typer.Argument(".", help="Target directory or file path to evaluate"),
    fix: bool = typer.Option(
        False, "--fix", "-f", help="Attempt semantic LLM auto-patch via local Ollama"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output full report in raw JSON format"
    ),
    severity: str | None = typer.Option(
        None,
        "--severity",
        "-s",
        help="Filter violations by minimum severity (INFO, WARNING, ERROR, CRITICAL)",
    ),
) -> None:
    """Evaluates target files against architectural, typing, security, and legal invariants."""
    target_path = Path(path)
    if not target_path.exists():
        console.print(f"[bold red]Error:[/bold red] Target path '{path}' does not exist.")
        raise typer.Exit(code=1)

    report = run_pipeline(target_path, auto_fix=fix)

    if json_output:
        console.print(report.model_dump_json(indent=2))
        sys.exit(0 if report.passed else 1)

    # Filter violations if severity threshold specified
    violations = report.violations
    if severity:
        sev_upper = severity.upper()
        violations = [v for v in violations if v.severity.value == sev_upper]

    console.print()
    console.print("[bold blue]🛡️  DevLab Guard — Autonomous Policy Evaluation[/bold blue]")
    console.print(
        f"Scanned [bold]{report.total_files_scanned}[/bold] files in [cyan]{report.execution_time_ms}ms[/cyan]."
    )
    console.print()

    if not violations:
        console.print(
            "[bold green]✅ All architectural and security invariant gates passed with 0 violations![/bold green]\n"
        )
        sys.exit(0)

    # Render Rich formatted table
    table = Table(title="Detected Policy Violations", show_header=True, header_style="bold magenta")
    table.add_column("Rule", style="cyan", width=9)
    table.add_column("Severity", width=10)
    table.add_column("Location", style="yellow")
    table.add_column("Description", style="white")

    severity_colors = {
        Severity.CRITICAL: "[bold red]CRITICAL[/bold red]",
        Severity.ERROR: "[red]ERROR[/red]",
        Severity.WARNING: "[yellow]WARNING[/yellow]",
        Severity.INFO: "[blue]INFO[/blue]",
    }

    for v in violations:
        sev_label = severity_colors.get(v.severity, v.severity.value)
        loc = f"{Path(v.file_path).name}:{v.line_number}"
        table.add_row(v.rule_id, sev_label, loc, v.message)

    console.print(table)
    console.print()

    if report.suggested_diff_patch:
        console.print(
            "[bold magenta]✨ Suggested Unified Git Diff Patch from Ollama:[/bold magenta]"
        )
        console.print(f"```diff\n{report.suggested_diff_patch}\n```\n")

    if not report.passed:
        console.print(
            f"[bold red]❌ Quality Gate FAILED with {report.total_violations} violations.[/bold red]\n"
        )
        sys.exit(1)
    else:
        console.print(
            "[bold yellow]⚠️ Completed with advisory warnings only (Non-blocking).[/bold yellow]\n"
        )
        sys.exit(0)


def main():
    """CLI entrypoint."""
    app()


if __name__ == "__main__":
    main()
