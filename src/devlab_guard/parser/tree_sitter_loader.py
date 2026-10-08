"""Dynamic Tree-sitter grammar loader and AST parser for TypeScript, Python, and Go.

Module: devlab_guard.parser.tree_sitter_loader
"""

from pathlib import Path

import tree_sitter_go as go_grammar
import tree_sitter_python as py_grammar
import tree_sitter_typescript as ts_grammar
from tree_sitter import Language, Parser, Tree

# Pre-compiled Tree-sitter Language singletons
_LANGUAGES: dict[str, Language] = {
    "typescript": Language(ts_grammar.language_typescript()),
    "tsx": Language(ts_grammar.language_tsx()),
    "python": Language(py_grammar.language()),
    "go": Language(go_grammar.language()),
}

# Extension to language mapping
_EXT_MAP: dict[str, str] = {
    ".ts": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".js": "typescript",
    ".mjs": "typescript",
    ".cjs": "typescript",
    ".tsx": "tsx",
    ".jsx": "tsx",
    ".py": "python",
    ".go": "go",
}


def get_language_for_path(file_path: Path | str) -> str | None:
    """Resolves the canonical language key based on file extension.

    Args:
        file_path: Target path to evaluate.

    Returns:
        Language name string if supported, otherwise None.
    """
    path = Path(file_path)
    return _EXT_MAP.get(path.suffix.lower())


def get_parser(language_key: str) -> Parser | None:
    """Retrieves a configured Parser initialized with the target grammar.

    Args:
        language_key: Identifier key from _LANGUAGES map.

    Returns:
        Parser instance or None if unsupported language.
    """
    lang = _LANGUAGES.get(language_key)
    if not lang:
        return None
    return Parser(lang)


def parse_source(source_code: str, file_path: Path | str) -> tuple[Tree | None, str | None]:
    """Parses raw source code into a Tree-sitter syntax tree.

    Args:
        source_code: String contents of the file.
        file_path: Source file path used for extension detection.

    Returns:
        Tuple containing the AST Tree (or None) and the language key.
    """
    lang_key = get_language_for_path(file_path)
    if not lang_key:
        return None, None

    parser = get_parser(lang_key)
    if not parser:
        return None, None

    tree = parser.parse(source_code.encode("utf-8"))
    return tree, lang_key
