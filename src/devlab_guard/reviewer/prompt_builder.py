"""Structured prompt composer for semantic LLM code review and automated remediation.

Module: devlab_guard.reviewer.prompt_builder
"""

from devlab_guard.core.models import Violation


def build_review_prompt(file_path: str, snippet: str, violations: list[Violation]) -> str:
    """Builds a zero-shot remediation prompt for local Ollama code models.

    Args:
        file_path: Target filename.
        snippet: Flagged code block.
        violations: List of violations triggered in this block.

    Returns:
        Formatted prompt string.
    """
    violation_lines = "\n".join(f"- [{v.rule_id}] {v.message}" for v in violations)

    return (
        "You are DevLab Guard, a strict Principal Architect.\n"
        f"File: {file_path}\n\n"
        "Violations identified:\n"
        f"{violation_lines}\n\n"
        "Problematic Code Snippet:\n"
        "```\n"
        f"{snippet}\n"
        "```\n\n"
        "Task: Output ONLY a unified git diff patch fixing the issues above with zero conversational commentary.\n"
    )
