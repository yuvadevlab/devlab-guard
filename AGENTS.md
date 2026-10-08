# DevLab Guard Agent Guidelines

Master guidelines for AI agents developing on **DevLab Guard (Autonomous AST Policy Enforcer & Security Scanner)**.

All agents must adhere to:
1. **Hard 250-Line Maximum Rule**: No Python file across `src/` may exceed 250 lines. Decompose early at 200 lines.
2. **Type Annotations & Docstrings**: Every function and class must have full Python type hints and Google/NumPy-style docstrings.
3. **Tooling Standards**: Python 3.12+, managed strictly with `uv` and formatted with `ruff`.
4. **Security Invariants**: High-speed AST scanning with Tree-sitter; zero false-negatives on Shannon entropy and PII scanners.
5. **Quality Gates & Conventional Commits**: All commits must pass git pre-commit hooks (`uv run ruff check`).
