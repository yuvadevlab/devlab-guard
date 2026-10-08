# DevLab Guard — Deep Product & Technical Specification Dossier

## 1. Product Overview & Vision

### 1.1 The Operational Problem Space
When multiple autonomous AI agents (such as Antigravity, Claude Code, GitHub Copilot) collaborate alongside human engineers in a high-scale monorepo ecosystem, architectural drift occurs rapidly:
- Agents tend to concatenate logic into giant 1,000+ line monolith files.
- Inlined string literals (e.g. `"completed"`, `"user"`) proliferate, bypassing typed domain enums.
- Code loses explanatory rationale, making future agent triage and reasoning uncertain.
- Inward dependency flows break when packages accidentally import application layers.

Standard linters (like ESLint or standard Ruff) check style, syntax, and basic bugs, but lack **semantic architectural governance rules** tailored to agentic development.

### 1.2 The DevLab Guard Solution
DevLab Guard is an **architectural AST governor**. Rather than checking simple whitespace or variable naming, Guard parses syntax trees to enforce deep structural invariants:
1. **The Hard 250-Line Maximum Rule**: Mathematically guarantees high cohesion and modularity by halting CI if any file exceeds 250 lines.
2. **Comment-to-Branch Density**: Inspects every conditional branch to ensure human- and agent-readable rationale exists.
3. **Canonical Enum Enforcement**: Guarantees zero magic numbers or naked status strings across distributed services.
4. **Clean Boundary Flow**: Asserts inward dependency boundaries across monorepos.

---

## 2. Technical Stack & Architectural Rationale

### 2.1 Language Choice: Python 3.12 with `uv` & `ruff`
- **Why Python for Static Analysis?**
  - **Native AST Standard Library**: Python's built-in `ast` module, `tokenize`, and `symtable` provide unparalleled introspection into code structure without needing external heavy language servers.
  - **Mature Static Analysis Ecosystem**: First-class support for syntax tree visitors, CST (Concrete Syntax Trees), and cross-compilation tree structures.
  - **Astral Toolchain Synergy (`uv` + `ruff`)**:
    - `uv` provides 10-100x faster package installation and virtualenv creation compared to pip/poetry, written in Rust.
    - `ruff` executes linter and formatter checks in single-digit milliseconds, enabling instant pre-commit validation.

### 2.2 AST Visitors vs Plain Regex Linters
| Feature | Plain Regex Linter | DevLab Guard AST Visitor |
| :--- | :--- | :--- |
| **Parsing Precision** | Brittle; fails on multi-line expressions, quotes, comments | Exact syntax tree representation |
| **Scope Awareness** | None (blind pattern match) | Full lexical scope, closure, and block awareness |
| **Line Counting** | Counts blank lines and comments indiscriminately | Accurately calculates logical SLOC vs documentation |
| **False Positive Rate** | High (>30% in complex codebases) | Near zero (<0.1%) |

---

## 3. Structural & Architectural Design

```
devlab-guard/
├── src/
│   ├── ast_parser/         # Multi-language AST generators & tokenizers
│   ├── rules/              # Modular visitor rule implementations
│   │   ├── line_count.py   # DL-001: 250-line rule verification
│   │   ├── comments.py     # DL-002: Control flow comment density check
│   │   ├── jsdoc.py        # DL-003: Exported symbol documentation check
│   │   ├── enums.py        # DL-004: Bare string & magic number detector
│   │   └── boundaries.py   # DL-005: Inward architecture flow inspector
│   ├── reporter/           # Terminal table formatter & SARIF JSON serializer
│   └── cli.py              # CLI router with colored terminal output
├── pyproject.toml          # uv package metadata
└── ruff.toml               # High-performance linter configuration
```

---

## 4. Integration into DevLab Ecosystem

DevLab Guard functions as the automated gatekeeper:
- **Git Pre-Commit**: Validates staged files within 300ms before allowing a commit.
- **CI / GitHub Actions**: Scans pull requests and generates inline SARIF annotations on offending lines.
- **DevLab Portal**: Feeds architectural health scores and compliance dashboards to enterprise admins.
