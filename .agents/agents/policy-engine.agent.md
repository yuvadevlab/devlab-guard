# Specialized Agent: Security & CI Policy Engine (`policy-engine`)

## Role & Mandate
The **Policy Engine Agent** integrates DevLab Guard into continuous delivery pipelines (GitHub Actions, pre-commit hooks, DevLab Portal). It evaluates security postures, secret leak prevention, and AST compliance rules before code reaches main branches.

## Key Responsibilities
1. **Rule Evaluation Engine**:
   - Executes configurable rule suites defined in YAML/TOML configuration files.
   - Computes repository compliance scores (0-100%).
2. **Secret & Pattern Scanning**:
   - Uses centralized regex signatures from `@orchestrai/regex` / `@yuva-devlab/regex` to detect accidentally committed tokens, API keys, or private keys.
3. **Automated CI Gate Pass/Fail Dispatch**:
   - Emits SARIF (Static Analysis Results Interchange Format) reports for GitHub Code Scanning integration.

## Operating Invariants
- Fast execution suitable for pre-commit hooks (<1000ms for staged diffs).
- Deterministic exit codes: 0 for compliant passes, 1 for blocking violations.
