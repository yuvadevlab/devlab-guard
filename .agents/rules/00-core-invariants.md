# Core Invariants — DevLab Guard

1. **250-Line Limit**: Every single file must stay strictly under 250 lines of code.
2. **Tree-sitter AST Scanning**:
   - Zero regex parsing for syntax rules; strictly use Tree-sitter AST queries.
3. **Ruff Formatting**:
   - Code must format cleanly via `uv run ruff format`.
   - Linting must pass with 0 warnings via `uv run ruff check`.
