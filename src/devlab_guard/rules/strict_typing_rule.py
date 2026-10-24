"""Rule TYPE001: Enforces strict typing, flags 'any' escapes and missing return annotations.

Module: devlab_guard.rules.strict_typing_rule
"""

from tree_sitter import Node, Tree

from devlab_guard.core.models import Severity, Violation, ViolationCategory
from devlab_guard.ui_copy import RULES


def _find_any_types(
    node: Node, source_bytes: bytes, file_path: str, violations: list[Violation]
) -> None:
    """Recursively walks AST searching for explicit 'any' type annotations."""
    if node.type == "predefined_type":
        text = source_bytes[node.start_byte : node.end_byte].decode("utf-8", "ignore")
        if text == "any":
            violations.append(
                Violation(
                    rule_id="TYPE001",
                    category=ViolationCategory.TYPING,
                    severity=Severity.ERROR,
                    file_path=file_path,
                    line_number=node.start_point.row + 1,
                    column=node.start_point.column,
                    message=RULES["ANY_MESSAGE"],
                    suggested_fix=RULES["ANY_FIX"],
                    code_snippet=source_bytes[
                        max(0, node.start_byte - 15) : min(len(source_bytes), node.end_byte + 15)
                    ].decode("utf-8", "ignore"),
                )
            )

    for child in node.children:
        _find_any_types(child, source_bytes, file_path, violations)


def evaluate_strict_typing(
    tree: Tree, source_bytes: bytes, file_path: str, language: str
) -> list[Violation]:
    """Validates type system invariants on TypeScript and Python source trees.

    Args:
        tree: Parsed Tree-sitter tree.
        source_bytes: UTF-8 encoded source bytes.
        file_path: Relative file path.
        language: Source language.

    Returns:
        List of typing violations found.
    """
    violations: list[Violation] = []
    if language in ("typescript", "tsx"):
        _find_any_types(tree.root_node, source_bytes, file_path, violations)
    return violations
