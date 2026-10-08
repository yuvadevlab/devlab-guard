"""SAST Prompt Safety Scanner detecting prompt injection risks in autonomous agent templates.

Module: devlab_guard.security.prompt_safety
"""

import re

from devlab_guard.core.models import Severity, Violation, ViolationCategory

# Patterns indicating unescaped user prompt injection risks in system templates
PROMPT_INJECTION_RISK_PATTERNS = [
    (
        r"system_prompt\s*=\s*f?['\"].*?\{user_input\}",
        "Unsanitized user_input interpolation in system prompt",
    ),
    (r"You are an AI.*?\$\{input\}", "Unbounded template interpolation in instruction prompt"),
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
                        message=f"Prompt injection vulnerability: {desc}.",
                        suggested_fix="Isolate user content within explicit delimiters (e.g. <user_query> tags) and sanitize inputs.",
                        code_snippet=line.strip()[:80],
                    )
                )

    return violations
