"""Rule ARCH003: Flags raw hardcoded string literals used for domain statuses and roles.

Module: devlab_guard.rules.enum_rule
"""

from tree_sitter import Node, Tree

from devlab_guard.core.models import Severity, Violation, ViolationCategory

FORBIDDEN_RAW_STATUS_STRINGS: set[str] = {
    '"completed"',
    '"failed"',
    '"pending"',
    '"running"',
    '"cancelled"',
    '"admin"',
    '"super_admin"',
    '"developer"',
    '"operator"',
}


def _check_string_comparisons(
    node: Node, source_bytes: bytes, file_path: str, violations: list[Violation]
) -> None:
    """Detects binary comparison expressions comparing variables to domain status strings."""
    if node.type == "binary_expression":
        # Check operator (===, ==, !==, !=)
        has_equality = any(
            source_bytes[c.start_byte : c.end_byte].decode("utf-8", "ignore")
            in ("===", "==", "!==", "!=")
            for c in node.children
            if c.type in ("===", "==", "!==", "!=")
        )

        if has_equality:
            for child in node.children:
                if child.type == "string":
                    text = source_bytes[child.start_byte : child.end_byte].decode("utf-8", "ignore")
                    if text.lower() in FORBIDDEN_RAW_STATUS_STRINGS:
                        violations.append(
                            Violation(
                                rule_id="ARCH003",
                                category=ViolationCategory.ARCHITECTURE,
                                severity=Severity.WARNING,
                                file_path=file_path,
                                line_number=child.start_point.row + 1,
                                column=child.start_point.column,
                                message=f"Raw domain string literal {text} used in equality comparison. Use canonical enum.",
                                suggested_fix="Replace with Enum.KEY (e.g. ExecutionStatus.COMPLETED or Role.ADMIN).",
                                code_snippet=source_bytes[node.start_byte : node.end_byte].decode(
                                    "utf-8", "ignore"
                                ),
                            )
                        )

    for child in node.children:
        _check_string_comparisons(child, source_bytes, file_path, violations)


def evaluate_enum_usage(
    tree: Tree, source_bytes: bytes, file_path: str, language: str
) -> list[Violation]:
    """Scans AST for anti-patterns involving bare status or role string literals."""
    violations: list[Violation] = []
    if language in ("typescript", "tsx", "python", "go"):
        _check_string_comparisons(tree.root_node, source_bytes, file_path, violations)
    return violations
