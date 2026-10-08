"""Legal & License Compliance Auditor preventing copyleft contamination (GPL, AGPL, SSPL).

Module: devlab_guard.legal.license_auditor
"""

import json
from pathlib import Path

from devlab_guard.core.config import FORBIDDEN_LICENSES
from devlab_guard.core.models import Severity, Violation, ViolationCategory


def audit_package_json(package_json_path: Path | str) -> list[Violation]:
    """Audits a package.json file for forbidden open-source licenses and metadata.

    Args:
        package_json_path: Filepath pointing to package.json.

    Returns:
        List of legal compliance violations.
    """
    path = Path(package_json_path)
    if not path.is_file():
        return []

    violations: list[Violation] = []
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
        declared_license = content.get("license")

        # 1. Check top-level package license
        if declared_license and declared_license in FORBIDDEN_LICENSES:
            violations.append(
                Violation(
                    rule_id="LEG001",
                    category=ViolationCategory.LEGAL,
                    severity=Severity.CRITICAL,
                    file_path=str(path),
                    line_number=1,
                    column=0,
                    message=f"Forbidden copyleft license declared: '{declared_license}'. Contaminates enterprise distribution.",
                    suggested_fix="Re-license package under an approved permissive license: MIT or Apache-2.0.",
                )
            )
    except Exception as err:
        violations.append(
            Violation(
                rule_id="LEG002",
                category=ViolationCategory.LEGAL,
                severity=Severity.WARNING,
                file_path=str(path),
                line_number=1,
                column=0,
                message=f"Failed to parse package.json for license auditing: {err}",
            )
        )

    return violations
