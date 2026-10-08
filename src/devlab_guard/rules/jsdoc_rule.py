"""Rule ARCH002: Mandates comprehensive JSDoc/docstrings on all exported symbols.

Module: devlab_guard.rules.jsdoc_rule
"""

from tree_sitter import Node, Tree

from devlab_guard.core.models import Severity, Violation, ViolationCategory


def _has_preceding_jsdoc(node: Node, source_bytes: bytes) -> bool:
    """Checks whether node is preceded by a block comment starting with /**."""
    prev = node.prev_sibling
    if prev and prev.type == "comment":
        comment_text = source_bytes[prev.start_byte : prev.end_byte].decode("utf-8", "ignore")
        return comment_text.strip().startswith("/**")
    return False


def _evaluate_ts_jsdoc(root_node: Node, source_bytes: bytes, file_path: str) -> list[Violation]:
    """Scans TypeScript AST for exported functions and classes missing JSDoc."""
    violations: list[Violation] = []

    for child in root_node.children:
        if child.type == "export_statement":
            # Search for declared symbol within export statement
            has_doc = _has_preceding_jsdoc(child, source_bytes)
            if not has_doc:
                # Find symbol name for high-clarity error message
                symbol_name = "exported_symbol"
                for sub in child.children:
                    if sub.type in (
                        "function_declaration",
                        "class_declaration",
                        "interface_declaration",
                    ):
                        for identifier in sub.children:
                            if (
                                identifier.type == "type_identifier"
                                or identifier.type == "identifier"
                            ):
                                symbol_name = source_bytes[
                                    identifier.start_byte : identifier.end_byte
                                ].decode("utf-8", "ignore")
                                break

                violations.append(
                    Violation(
                        rule_id="ARCH002",
                        category=ViolationCategory.ARCHITECTURE,
                        severity=Severity.WARNING,
                        file_path=file_path,
                        line_number=child.start_point.row + 1,
                        column=child.start_point.column,
                        message=f"Exported symbol '{symbol_name}' is missing a JSDoc docstring block.",
                        suggested_fix=f"Add a '/** ... */' JSDoc comment describing '{symbol_name}' parameters and return contract.",
                        code_snippet=source_bytes[
                            child.start_byte : min(child.start_byte + 80, child.end_byte)
                        ].decode("utf-8", "ignore"),
                    )
                )

    return violations


def _evaluate_py_docstrings(
    root_node: Node, source_bytes: bytes, file_path: str
) -> list[Violation]:
    """Scans Python AST for top-level functions and classes missing docstrings."""
    violations: list[Violation] = []

    for child in root_node.children:
        if child.type in ("function_definition", "class_definition"):
            # Check if first body statement is a docstring
            body = None
            for sub in child.children:
                if sub.type == "block":
                    body = sub
                    break

            has_docstring = False
            if body and body.children:
                first_stmt = body.children[0]
                if first_stmt.type == "expression_statement":
                    for expr_child in first_stmt.children:
                        if expr_child.type == "string":
                            has_docstring = True
                            break

            if not has_docstring:
                # Extract function or class name
                name = "symbol"
                for sub in child.children:
                    if sub.type == "identifier":
                        name = source_bytes[sub.start_byte : sub.end_byte].decode("utf-8", "ignore")
                        break

                violations.append(
                    Violation(
                        rule_id="ARCH002",
                        category=ViolationCategory.ARCHITECTURE,
                        severity=Severity.WARNING,
                        file_path=file_path,
                        line_number=child.start_point.row + 1,
                        column=child.start_point.column,
                        message=f"Python definition '{name}' lacks a comprehensive docstring.",
                        suggested_fix=f"Add a triple-quoted docstring at the top of '{name}'.",
                    )
                )

    return violations


def evaluate_docstrings(
    tree: Tree, source_bytes: bytes, file_path: str, language: str
) -> list[Violation]:
    """Evaluates AST docstring coverage according to language conventions."""
    if language in ("typescript", "tsx"):
        return _evaluate_ts_jsdoc(tree.root_node, source_bytes, file_path)
    if language == "python":
        return _evaluate_py_docstrings(tree.root_node, source_bytes, file_path)
    return []
