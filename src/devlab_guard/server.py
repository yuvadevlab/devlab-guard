"""FastAPI Webhook and CI/CD REST server for automated PR policy enforcement.

Module: devlab_guard.server
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from devlab_guard.core.models import GuardReport
from devlab_guard.core.pipeline import run_pipeline
from devlab_guard.ui_copy import API

app = FastAPI(
    title=API["TITLE"],
    description=API["DESCRIPTION"],
    version="1.0.0",
)


class ScanRequest(BaseModel):
    """Payload specifying file or directory to scan."""

    target_path: str = Field(description=API["TARGET_PATH"])
    auto_fix: bool = Field(default=False, description=API["AUTO_FIX"])


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
            status_code=404,
            detail=API["MISSING_PATH"].format(path=request.target_path),
        )

    return run_pipeline(target, auto_fix=request.auto_fix)
