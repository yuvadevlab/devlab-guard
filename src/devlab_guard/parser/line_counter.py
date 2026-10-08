"""Accurate line counter isolating executable source statements from blanks and trivia comments.

Module: devlab_guard.parser.line_counter
"""

from dataclasses import dataclass


@dataclass
class LineCount:
    """Breakdown of line metrics for a scanned source file."""

    total_lines: int
    executable_lines: int
    comment_lines: int
    blank_lines: int


def count_lines(content: str, language: str) -> LineCount:
    """Analyzes source file text and categorizes each line.

    Args:
        content: Raw source string.
        language: Canonical language identifier (e.g. typescript, python, go).

    Returns:
        LineCount dataclass containing metric breakdowns.
    """
    lines: list[str] = content.splitlines()
    total = len(lines)
    blank = 0
    comment = 0
    executable = 0
    in_multiline_comment = False

    for line in lines:
        stripped = line.strip()

        # 1. Blank line check
        if not stripped:
            blank += 1
            continue

        # 2. Multiline comment tracking for C-style languages
        if language in ("typescript", "tsx", "go"):
            if in_multiline_comment:
                comment += 1
                if "*/" in stripped:
                    in_multiline_comment = False
                continue
            if stripped.startswith("/*"):
                comment += 1
                if "*/" not in stripped:
                    in_multiline_comment = True
                continue
            if stripped.startswith("//"):
                comment += 1
                continue

        # 3. Python comment tracking
        if language == "python":
            if stripped.startswith("#"):
                comment += 1
                continue

        executable += 1

    return LineCount(
        total_lines=total,
        executable_lines=executable,
        comment_lines=comment,
        blank_lines=blank,
    )
