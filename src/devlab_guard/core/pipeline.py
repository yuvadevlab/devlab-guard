"""Master evaluation pipeline orchestrating AST traversal, SAST security, and legal audit rules.

Module: devlab_guard.core.pipeline
"""

import time
from pathlib import Path

from devlab_guard.core.models import GuardReport, Severity, Violation
from devlab_guard.legal.license_auditor import audit_package_json
from devlab_guard.legal.pii_auditor import scan_pii
from devlab_guard.parser.tree_sitter_loader import get_language_for_path, parse_source
from devlab_guard.reviewer.client import OllamaClient
from devlab_guard.reviewer.patch_generator import extract_diff_patch
from devlab_guard.reviewer.prompt_builder import build_review_prompt
from devlab_guard.rules.enum_rule import evaluate_enum_usage
from devlab_guard.rules.jsdoc_rule import evaluate_docstrings
from devlab_guard.rules.line_limit_rule import evaluate_line_limit
from devlab_guard.rules.strict_typing_rule import evaluate_strict_typing
from devlab_guard.security.injection_scanner import scan_for_injections
from devlab_guard.security.prompt_safety import scan_prompt_safety
from devlab_guard.security.secret_scanner import scan_for_secrets

IGNORED_DIRECTORIES: set[str] = {
    "node_modules",
    ".git",
    "dist",
    ".next",
    ".venv",
    ".turbo",
    "build",
    ".cache",
    "coverage",
    "__pycache__",
}


def scan_file(file_path: Path) -> list[Violation]:
    """Applies all applicable architectural, security, and legal rules to a single file."""
    violations: list[Violation] = []
    str_path = str(file_path)

    # 1. Legal license check on package.json
    if file_path.name == "package.json":
        return audit_package_json(file_path)

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    # 2. Text-level scanners (Secrets, PII, Prompt Safety)
    violations.extend(scan_for_secrets(str_path, content))
    violations.extend(scan_pii(str_path, content))
    violations.extend(scan_prompt_safety(str_path, content))

    language = get_language_for_path(file_path)
    if not language:
        return violations

    # 3. Line Limit Rule (ARCH001)
    violations.extend(evaluate_line_limit(str_path, content, language))

    # 4. AST-level scanners via Tree-sitter
    tree, _ = parse_source(content, file_path)
    if tree:
        source_bytes = content.encode("utf-8")
        violations.extend(evaluate_docstrings(tree, source_bytes, str_path, language))
        violations.extend(evaluate_strict_typing(tree, source_bytes, str_path, language))
        violations.extend(evaluate_enum_usage(tree, source_bytes, str_path, language))
        violations.extend(scan_for_injections(tree, source_bytes, str_path))

    return violations


def run_pipeline(target_path: Path | str, auto_fix: bool = False) -> GuardReport:
    """Executes the full DevLab Guard evaluation pipeline across a file or repository.

    Args:
        target_path: Path to target file or root repository directory.
        auto_fix: If True, attempts to query local Ollama to generate unified git diff patches.

    Returns:
        Comprehensive GuardReport model.
    """
    start_time = time.perf_counter()
    path = Path(target_path).resolve()
    all_violations: list[Violation] = []
    scanned_count = 0

    if path.is_file():
        all_violations.extend(scan_file(path))
        scanned_count = 1
    elif path.is_dir():
        for item in path.rglob("*"):
            if item.is_file():
                if any(ignored in item.parts for ignored in IGNORED_DIRECTORIES):
                    continue
                file_violations = scan_file(item)
                all_violations.extend(file_violations)
                scanned_count += 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    # Passed if zero ERROR or CRITICAL severity violations are found
    has_blocking_errors = any(
        v.severity in (Severity.ERROR, Severity.CRITICAL) for v in all_violations
    )

    suggested_patch = None
    if auto_fix and all_violations:
        ollama = OllamaClient()
        if ollama.is_available():
            top_v = all_violations[0]
            snippet = top_v.code_snippet or "Snippet unavailable"
            prompt = build_review_prompt(top_v.file_path, snippet, [top_v])
            raw_patch = ollama.generate_fix(prompt)
            if raw_patch:
                suggested_patch = extract_diff_patch(raw_patch)

    return GuardReport(
        total_files_scanned=scanned_count,
        total_violations=len(all_violations),
        passed=not has_blocking_errors,
        violations=all_violations,
        suggested_diff_patch=suggested_patch,
        execution_time_ms=round(elapsed_ms, 2),
    )
