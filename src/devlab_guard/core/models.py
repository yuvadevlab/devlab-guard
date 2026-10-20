"""Pydantic v2 schemas and canonical enums for DevLab Guard violation reporting.

Module: devlab_guard.core.models
"""

from enum import StrEnum

from pydantic import BaseModel, Field

from devlab_guard.ui_copy import SCHEMA


class Severity(StrEnum):
    """Severity classification for policy violations."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ViolationCategory(StrEnum):
    """Categorical taxonomy for architectural and security policy infractions."""

    ARCHITECTURE = "ARCHITECTURE"
    SECURITY = "SECURITY"
    LEGAL = "LEGAL"
    TYPING = "TYPING"


class Violation(BaseModel):
    """Individual code violation identified by an AST or SAST evaluation rule."""

    rule_id: str = Field(description=SCHEMA["RULE_ID"])
    category: ViolationCategory = Field(description=SCHEMA["CATEGORY"])
    severity: Severity = Field(description=SCHEMA["SEVERITY"])
    file_path: str = Field(description=SCHEMA["FILE_PATH"])
    line_number: int = Field(ge=1, description=SCHEMA["LINE_NUMBER"])
    column: int = Field(default=0, ge=0, description=SCHEMA["COLUMN"])
    message: str = Field(description=SCHEMA["MESSAGE"])
    suggested_fix: str | None = Field(default=None, description=SCHEMA["SUGGESTED_FIX"])
    code_snippet: str | None = Field(default=None, description=SCHEMA["CODE_SNIPPET"])


class RuleResult(BaseModel):
    """Intermediate execution result aggregated from a single rule evaluator."""

    rule_id: str
    violations: list[Violation] = Field(default_factory=list)


class GuardReport(BaseModel):
    """Comprehensive evaluation report summarizing whole repository health and scan results."""

    total_files_scanned: int = Field(ge=0)
    total_violations: int = Field(ge=0)
    passed: bool = Field(description=SCHEMA["PASSED"])
    violations: list[Violation] = Field(default_factory=list)
    suggested_diff_patch: str | None = Field(default=None, description=SCHEMA["PATCH"])
    execution_time_ms: float = Field(ge=0.0)
