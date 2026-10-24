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
from devlab_guard.ui_copy import CLI

app = typer.Typer(
    name="guard",
    help=CLI["APP_HELP"],
    no_args_is_help=True,
)
console = Console()


@app.command(name="check")
def check(
    path: str = typer.Argument(".", help=CLI["TARGET_HELP"]),
    fix: bool = typer.Option(False, "--fix", "-f", help=CLI["FIX_HELP"]),
    json_output: bool = typer.Option(False, "--json", "-j", help=CLI["JSON_HELP"]),
    severity: str | None = typer.Option(
        None,
        "--severity",
        "-s",
        help=CLI["SEVERITY_HELP"],
    ),
) -> None:
    """Evaluates target files against architectural, typing, security, and legal invariants."""
    target_path = Path(path)
    if not target_path.exists():
        console.print(CLI["MISSING_PATH"].format(path=path))
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
    console.print(CLI["BANNER"])
    console.print(
        CLI["SCAN_SUMMARY"].format(
            total=report.total_files_scanned,
            duration=report.execution_time_ms,
        )
    )
    console.print()

    if not violations:
        console.print(CLI["PASSED"])
        sys.exit(0)

    # Render Rich formatted table
    table = Table(title=CLI["TABLE_TITLE"], show_header=True, header_style="bold magenta")
    table.add_column(CLI["COLUMN_RULE"], style="cyan", width=9)
    table.add_column(CLI["COLUMN_SEVERITY"], width=10)
    table.add_column(CLI["COLUMN_LOCATION"], style="yellow")
    table.add_column(CLI["COLUMN_DESCRIPTION"], style="white")

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
        console.print(CLI["PATCH_TITLE"])
        console.print(CLI["PATCH_FORMAT"].format(patch=report.suggested_diff_patch))

    if not report.passed:
        console.print(CLI["FAILED"].format(count=report.total_violations))
        sys.exit(1)
    else:
        console.print(CLI["WARNINGS"])
        sys.exit(0)


def main():
    """CLI entrypoint."""
    app()


if __name__ == "__main__":
    main()
