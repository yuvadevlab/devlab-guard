"""SAST Secret Scanner utilizing Shannon entropy and signature matching to detect leaked credentials.

Module: devlab_guard.security.secret_scanner
"""

import math
import re

from devlab_guard.core.config import SHANNON_ENTROPY_THRESHOLD
from devlab_guard.core.models import Severity, Violation, ViolationCategory

# Known credential prefixes and signature regexes
SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"dlk_(?:live|dev)_[a-zA-Z0-9]{32,}", "DevLab Platform API Key"),
    (r"sk-[a-zA-Z0-9]{32,}", "OpenAI / Cloud Secret Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key Identifier"),
    (r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "Raw Private Key PEM Block"),
]


def calculate_shannon_entropy(data: str) -> float:
    """Computes the Shannon entropy of a string."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    frequencies = {char: data.count(char) for char in set(data)}
    for count in frequencies.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def scan_for_secrets(file_path: str, content: str) -> list[Violation]:
    """Scans raw file lines for high-entropy secrets and credential signatures."""
    violations: list[Violation] = []
    lines = content.splitlines()

    for line_idx, line in enumerate(lines, start=1):
        # 1. Pattern signature matching
        for pattern, desc in SECRET_PATTERNS:
            match = re.search(pattern, line)
            if match:
                violations.append(
                    Violation(
                        rule_id="SEC001",
                        category=ViolationCategory.SECURITY,
                        severity=Severity.CRITICAL,
                        file_path=file_path,
                        line_number=line_idx,
                        column=match.start(),
                        message=f"Hardcoded credential detected: {desc}.",
                        suggested_fix="Store credential in .env or cloud secret vault and load via environment variable.",
                        code_snippet=line.strip()[:80],
                    )
                )

        # 2. Shannon entropy check on quoted string literals
        for string_match in re.finditer(r"['\"]([a-zA-Z0-9_\-\.]{24,})['\"]", line):
            candidate = string_match.group(1)
            entropy = calculate_shannon_entropy(candidate)
            # High entropy tokens (> 4.2) that aren't simple English words
            if entropy >= SHANNON_ENTROPY_THRESHOLD:
                # Avoid duplicate flagging if already caught by signature
                if not any(v.line_number == line_idx and v.rule_id == "SEC001" for v in violations):
                    violations.append(
                        Violation(
                            rule_id="SEC002",
                            category=ViolationCategory.SECURITY,
                            severity=Severity.CRITICAL,
                            file_path=file_path,
                            line_number=line_idx,
                            column=string_match.start(),
                            message=f"High-entropy token detected (entropy {entropy:.2f}): possible secret leak.",
                            suggested_fix="Ensure high-entropy token is replaced with runtime environment variable.",
                            code_snippet=line.strip()[:80],
                        )
                    )

    return violations
