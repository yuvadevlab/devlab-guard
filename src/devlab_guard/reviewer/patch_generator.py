"""Parses and sanitizes LLM output into clean unified git diff patches.

Module: devlab_guard.reviewer.patch_generator
"""

import re


def extract_diff_patch(raw_llm_output: str) -> str | None:
    """Extracts unified diff content from LLM response, stripping markdown fences.

    Args:
        raw_llm_output: String returned from LLM generation.

    Returns:
        Sanitized unified git diff string or None.
    """
    if not raw_llm_output:
        return None

    # Check for markdown fenced code blocks (```diff ... ``` or ``` ...)
    fenced_match = re.search(r"```(?:diff)?\s*\n(.*?)\n```", raw_llm_output, re.DOTALL)
    if fenced_match:
        content = fenced_match.group(1).strip()
    else:
        content = raw_llm_output.strip()

    # Validate that output contains git diff markers
    if "---" in content or "+++" in content or "@@" in content:
        return content

    return None
