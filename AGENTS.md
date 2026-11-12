# DevLab Guard Agent Guidelines

Master guidelines for AI agents developing on **DevLab Guard (Autonomous AST Policy Enforcer & Security Scanner)**.

All agents must adhere to:

0. **Zero Commits Without Explicit Confirmation (CRITICAL)**:
   - NEVER execute `git commit`, `git push`, or open pull requests in ANY repository unless the user explicitly commands it in the current turn (e.g. "commit these changes", "commit and push").
   - Directives like "start", "proceed", "fix this", "implement", "build", or "test" authorize implementation, building, and running tests ONLY.
   - Always leave changes staged or in the working tree, present verification results, and wait for confirmation.
1. **Organization Standards & `.github` Inheritance**:
   - Standardize all author and committer attribution to `yuva.devlab@gmail.com`.
   - Branch naming must strictly follow: `^(feat|fix|refactor|perf|chore|docs|test|ci|hotfix)/[a-z0-9-]+$`.
   - PR descriptions must adhere to the 5-section high-signal standard defined in `yuvadevlab/.github` (Summary, Changes, How to Test, Proof of Verification, Risks).
   - Commits must conform to Conventional Commits: `<type>(<optional-scope>): <imperative summary>`.
2. **Pure Platform CSS & Framework Invariant**:
   - Zero references to legacy utility-first CSS frameworks across codebase, comments, or documentation.
3. **Hard 250-Line Maximum Rule**: No Python file across `src/` may exceed 250 lines. Decompose early at 200 lines.
4. **Type Annotations & Docstrings**: Every function and class must have full Python type hints and Google/NumPy-style docstrings.
5. **Tooling Standards**: Python 3.12+, managed strictly with `uv` and formatted with `ruff`.
6. **Security Invariants**: High-speed AST scanning with Tree-sitter; zero false-negatives on Shannon entropy and PII scanners.
7. **Quality Gates & Conventional Commits**: All commits must pass git pre-commit hooks (`uv run ruff check`).
8. **Strict User-Facing Copy Centralization Invariant**:
   - ALL user-facing CLI output, status strings, error messages, and prompt copy MUST be centralized in dedicated copy/constants modules.
   - Direct raw hardcoded user-facing strings scattered across core scanner algorithms are strictly prohibited.
