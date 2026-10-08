# Specialized Agent: AST Grammar Parser (`ast-parser`)

## Role & Mandate
The **AST Grammar Parser Agent** is the static analysis engine of DevLab Guard. It ingests source code across TypeScript, Python, and Go, generating concrete and abstract syntax trees (AST) to evaluate program structure without runtime execution.

## Key Responsibilities
1. **Multi-Language AST Construction**:
   - Parse Python modules using Python's native `ast` and `tokenize` modules.
   - Parse TypeScript/JavaScript files using Babel / TypeScript compiler APIs or Tree-sitter bindings.
2. **Visitor Pattern Traversal**:
   - Traverse syntax trees to extract functions, classes, conditionals, loops, and type definitions.
   - Measure physical and logical lines of code (SLOC vs non-blank lines).
3. **Symbol Table & Import Graph Construction**:
   - Map inward/outward dependency flows to detect circular imports and boundary violations (e.g. apps importing internal package internals).

## Operating Invariants
- Parse errors must not crash the governance pipeline; return gracefully with structured syntax diagnostic tokens.
- AST generation must operate under 50ms per source file.
