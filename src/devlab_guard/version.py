"""Application version and build metadata for DevLab Guard.

Implements Big Tech hybrid SemVer + Git SHA observability without hardcoded strings.
Module: devlab_guard.version
"""

import os
from importlib import metadata

try:
    __version__ = metadata.version("devlab-guard")
except metadata.PackageNotFoundError:
    __version__ = "0.1.0"

_git_sha = os.environ.get("GIT_SHA") or os.environ.get("NEXT_PUBLIC_GIT_SHA") or ""
GUARD_VERSION = os.environ.get("APP_VERSION") or (
    f"v{__version__}+{_git_sha[:7]}" if _git_sha else f"v{__version__}"
)

BUILD_METADATA = {
    "version": f"v{__version__}",
    "git_commit": _git_sha[:7] if _git_sha else "dev-local",
    "environment": os.environ.get("ENVIRONMENT", "development"),
}
