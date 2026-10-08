"""Recursive Visitor Pattern implementation for traversing Tree-sitter AST nodes.

Module: devlab_guard.parser.ast_visitor
"""

from tree_sitter import Node

from devlab_guard.core.models import Violation


class ASTVisitor:
    """Base AST visitor providing dynamic node dispatch and violation collection."""

    def __init__(self, source_bytes: bytes, file_path: str):
        self.source_bytes = source_bytes
        self.file_path = file_path
        self.violations: list[Violation] = []

    def get_node_text(self, node: Node) -> str:
        """Extracts UTF-8 text represented by the node range in source code."""
        return self.source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")

    def visit(self, node: Node) -> None:
        """Dispatches node to specialized visit_<type> handler or generic_visit.

        Args:
            node: Current Tree-sitter AST node.
        """
        method_name = f"visit_{node.type}"
        visitor_fn = getattr(self, method_name, self.generic_visit)
        visitor_fn(node)

    def generic_visit(self, node: Node) -> None:
        """Default fallback traversing all immediate children in document order.

        Args:
            node: Parent Tree-sitter AST node.
        """
        for child in node.children:
            self.visit(child)
