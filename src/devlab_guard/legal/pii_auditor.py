"""PII Auditor detecting unredacted Personally Identifiable Information (SSNs, Credit Cards).

Module: devlab_guard.legal.pii_auditor
"""

import re

from devlab_guard.core.models import Severity, Violation, ViolationCategory

SSN_REGEX = re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")
CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")


def _luhn_checksum(card_number: str) -> bool:
    """Validates whether digit sequence passes the Luhn check formula."""
    digits = [int(c) for c in card_number if c.isdigit()]
    if len(digits) not in (13, 14, 15, 16):
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0


def scan_pii(file_path: str, content: str) -> list[Violation]:
    """Scans raw file lines for unmasked SSNs and Luhn-valid credit card numbers."""
    violations: list[Violation] = []
    lines = content.splitlines()

    for line_idx, line in enumerate(lines, start=1):
        # 1. Social Security Number scan
        ssn_match = SSN_REGEX.search(line)
        if ssn_match:
            violations.append(
                Violation(
                    rule_id="LEG003",
                    category=ViolationCategory.LEGAL,
                    severity=Severity.CRITICAL,
                    file_path=file_path,
                    line_number=line_idx,
                    column=ssn_match.start(),
                    message="Hardcoded Social Security Number (SSN) detected in source code.",
                    suggested_fix="Mask or redact SSN identifier immediately.",
                    code_snippet=line.strip()[:80],
                )
            )

        # 2. Credit Card number scan with Luhn verification
        for card_match in CARD_REGEX.finditer(line):
            candidate = card_match.group(0)
            if _luhn_checksum(candidate):
                violations.append(
                    Violation(
                        rule_id="LEG004",
                        category=ViolationCategory.LEGAL,
                        severity=Severity.CRITICAL,
                        file_path=file_path,
                        line_number=line_idx,
                        column=card_match.start(),
                        message="Valid Payment Card Number detected in source code.",
                        suggested_fix="Mask or tokenize primary account number (PAN) per PCI-DSS standards.",
                        code_snippet=line.strip()[:80],
                    )
                )

    return violations
