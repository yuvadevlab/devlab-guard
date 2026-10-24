"""Rule ARCH001: Strict 250-Line Limit enforcer with progressive warning threshold.

Module: devlab_guard.rules.line_limit_rule
"""

from devlab_guard.core.config import MAX_FILE_LINES, WARNING_FILE_LINES
from devlab_guard.core.models import Severity, Violation, ViolationCategory
from devlab_guard.parser.line_counter import count_lines
from devlab_guard.ui_copy import RULES


def evaluate_line_limit(file_path: str, content: str, language: str) -> list[Violation]:
    """Validates file length invariants across all project source files.

    Args:
        file_path: Path to the target file.
        content: Raw source string.
        language: Detected programming language.

    Returns:
        List of Violation models if thresholds are exceeded.
    """
    counts = count_lines(content, language)
    violations: list[Violation] = []

    # 1. Hard invariant check: strictly > 250 lines fails build
    if counts.total_lines > MAX_FILE_LINES:
        violations.append(
            Violation(
                rule_id="ARCH001",
                category=ViolationCategory.ARCHITECTURE,
                severity=Severity.ERROR,
                file_path=file_path,
                line_number=MAX_FILE_LINES + 1,
                column=0,
                message=RULES["LINE_LIMIT_MESSAGE"](
                    counts.total_lines,
                    counts.executable_lines,
                ),
                suggested_fix=RULES["LINE_LIMIT_FIX"],
            )
        )
    # 2. Advisory warning: between 200 and 250 lines triggers proactive refactoring notice
    elif counts.total_lines > WARNING_FILE_LINES:
        violations.append(
            Violation(
                rule_id="ARCH001",
                category=ViolationCategory.ARCHITECTURE,
                severity=Severity.WARNING,
                file_path=file_path,
                line_number=WARNING_FILE_LINES + 1,
                column=0,
                message=RULES["LINE_WARNING"](counts.total_lines),
                suggested_fix=RULES["LINE_WARNING_FIX"],
            )
        )

    return violations
