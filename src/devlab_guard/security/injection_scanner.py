"""SAST Injection Scanner flagging SQL injection, command injection, and unsafe DOM manipulations.

Module: devlab_guard.security.injection_scanner
"""

from tree_sitter import Node, Tree

from devlab_guard.core.models import Severity, Violation, ViolationCategory

DANGEROUS_CALLS: set[str] = {
    "queryRawUnsafe",
    "rawQuery",
    "queryRaw",
    "exec",
    "execSync",
    "system",
    "popen",
}


def _extract_callee_name(callee_node: Node, source_bytes: bytes) -> str:
    """Extracts function name from direct call or member property call."""
    if callee_node.type in ("identifier", "property_identifier"):
        return source_bytes[callee_node.start_byte : callee_node.end_byte].decode("utf-8", "ignore")
    if callee_node.type == "member_expression":
        for child in callee_node.children:
            if child.type == "property_identifier":
                return source_bytes[child.start_byte : child.end_byte].decode("utf-8", "ignore")
    return ""


def _check_dangerous_calls(
    node: Node, source_bytes: bytes, file_path: str, violations: list[Violation]
) -> None:
    """Traverses AST call expressions to identify raw interpolation in sinks."""
    if node.type in ("call_expression", "call") and node.children:
        callee = node.children[0]
        fn_name = _extract_callee_name(callee, source_bytes)

        if fn_name in DANGEROUS_CALLS:
            args = [c for c in node.children if c.type in ("arguments", "argument_list")]
            for arg_list in args:
                for arg in arg_list.children:
                    if arg.type in ("template_string", "binary_expression"):
                        violations.append(
                            Violation(
                                rule_id="SEC003",
                                category=ViolationCategory.SECURITY,
                                severity=Severity.CRITICAL,
                                file_path=file_path,
                                line_number=node.start_point.row + 1,
                                column=node.start_point.column,
                                message=f"Potential injection risk in dangerous call '{fn_name}' with unparameterized dynamic string.",
                                suggested_fix="Use parameterized queries or prepared statements instead of string concatenation.",
                                code_snippet=source_bytes[node.start_byte : node.end_byte].decode(
                                    "utf-8", "ignore"
                                )[:90],
                            )
                        )

    for child in node.children:
        _check_dangerous_calls(child, source_bytes, file_path, violations)


def scan_for_injections(tree: Tree, source_bytes: bytes, file_path: str) -> list[Violation]:
    """Evaluates the entire AST for injection vulnerabilities."""
    violations: list[Violation] = []
    _check_dangerous_calls(tree.root_node, source_bytes, file_path, violations)
    return violations
