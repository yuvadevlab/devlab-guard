# Core Invariants — DevLab Guard

## 0. Strict Git Commit & Push Restriction (CRITICAL)

- **NEVER** run `git commit`, `git push`, or create pull requests without explicit, affirmative user authorization in the current turn.
- General task triggers like "start", "proceed", or "fix" authorize code authoring, linting, and testing ONLY.
- Changes must remain in the working tree or staging until the user explicitly commands to commit.

## 1. 250-Line Limit
- Every single file must stay strictly under 250 lines of code. Deconstruct early at 200 lines.

## 2. Organization Standards & .github Inheritance
- **Attribution**: Author and committer metadata standardized to `yuva.devlab@gmail.com`.
- **Branch Naming**: Must strictly follow: `^(feat|fix|refactor|perf|chore|docs|test|ci|hotfix)/[a-z0-9-]+$`.
- **Pull Requests**: Must conform to the 5-section high-signal template in `yuvadevlab/.github` (Summary, Changes, How to Test, Proof of Verification, Risks).
- **Conventional Commits**: `<type>(<optional-scope>): <imperative summary>`.
- **Pure Platform CSS**: Zero references to legacy utility-first CSS frameworks across codebase, comments, or documentation.

## 3. Tree-sitter AST Scanning
- Zero regex parsing for syntax rules; strictly use Tree-sitter AST queries.

## 4. Ruff Formatting & Tooling
- Code must format cleanly via `uv run ruff format`.
- Linting must pass with 0 warnings via `uv run ruff check`.
- Python 3.12+ managed strictly with `uv`.

## 5. Enums Over Raw String Unions & URL Key Centralization
- Prefer `enum`s or canonical dictionaries over raw string literal unions so changing underlying values only requires updating the definition.
- Never hardcode raw URL query parameter strings or fragments; use centralized constants/enums.

## 6. Semantic Component Architecture & 90/10 Hybrid Styling Standard
- UI components must declare purpose-revealing semantic classes defined in domain-scoped modular stylesheets (< 200 lines, strictly < 250 lines) under @layer dl-components.
- Multi-class utility soup in JSX is strictly prohibited; utilities are reserved exclusively for macro layout orchestration (10% glue).
- Component themes and variants must be parameterized via CSS variables mapped to @yuva-devlab/tokens.
