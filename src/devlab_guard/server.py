"""FastAPI Webhook and CI/CD REST server for automated PR policy enforcement.

Module: devlab_guard.server
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from devlab_guard.core.models import GuardReport
from devlab_guard.core.pipeline import run_pipeline

app = FastAPI(
    title="DevLab Guard API",
    description="Automated Security & Architecture Policy Reviewer",
    version="1.0.0",
)


class ScanRequest(BaseModel):
    """Payload specifying file or directory to scan."""

    target_path: str = Field(description="Local file or directory path")
    auto_fix: bool = Field(default=False, description="Attempt automated LLM fix")


class HealthResponse(BaseModel):
    """Basic service health status."""

    status: str
    version: str


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Returns service health status."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/api/v1/scan", response_model=GuardReport)
def scan_endpoint(request: ScanRequest) -> GuardReport:
    """Executes full evaluation pipeline on the specified target path."""
    target = Path(request.target_path)
    if not target.exists():
        raise HTTPException(
            status_code=404, detail=f"Target path '{request.target_path}' not found"
        )

    return run_pipeline(target, auto_fix=request.auto_fix)
