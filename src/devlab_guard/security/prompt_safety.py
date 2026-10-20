"""SAST Prompt Safety Scanner detecting prompt injection risks in autonomous agent templates.

Module: devlab_guard.security.prompt_safety
"""

import re

from devlab_guard.core.models import Severity, Violation, ViolationCategory
from devlab_guard.ui_copy import SECURITY

# Patterns indicating unescaped user prompt injection risks in system templates
PROMPT_INJECTION_RISK_PATTERNS = [
    (
        r"system_prompt\s*=\s*f?['\"].*?\{user_input\}",
        SECURITY["PROMPT_LABELS"]["UNSANITIZED_INPUT"],
    ),
    (
        r"You are an AI.*?\$\{input\}",
        SECURITY["PROMPT_LABELS"]["UNBOUNDED_INTERPOLATION"],
    ),
]


def scan_prompt_safety(file_path: str, content: str) -> list[Violation]:
    """Scans source content for unconstrained prompt template interpolations."""
    violations: list[Violation] = []
    lines = content.splitlines()

    for line_idx, line in enumerate(lines, start=1):
        for pattern, desc in PROMPT_INJECTION_RISK_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                violations.append(
                    Violation(
                        rule_id="SEC004",
                        category=ViolationCategory.SECURITY,
                        severity=Severity.WARNING,
                        file_path=file_path,
                        line_number=line_idx,
                        column=match.start(),
                        message=SECURITY["PROMPT_MESSAGE"](desc),
                        suggested_fix=SECURITY["PROMPT_FIX"],
                        code_snippet=line.strip()[:80],
                    )
                )

    return violations
