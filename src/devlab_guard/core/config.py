"""Central configuration parameters, thresholds, and compliance whitelists for DevLab Guard.

Module: devlab_guard.core.config
"""

import os
from typing import Final

# DevLab Ecosystem Service Configuration
DEVLAB_PORTAL_URL: Final[str] = os.getenv("DEVLAB_PORTAL_URL", "http://localhost:3015")
DEVLAB_GUARD_API_KEY: Final[str] = os.getenv("DEVLAB_GUARD_API_KEY", "")
PORT: Final[int] = int(os.getenv("PORT", "8000"))

# Hard limits for code cleanliness and modularity
MAX_FILE_LINES: Final[int] = 250
WARNING_FILE_LINES: Final[int] = 200
MAX_CYCLOMATIC_COMPLEXITY: Final[int] = 15

# Cryptographic Shannon entropy threshold for secret scanning
# Strings with entropy above 4.2 are likely high-entropy API tokens or credentials
SHANNON_ENTROPY_THRESHOLD: Final[float] = 4.2

# Open-source license governance whitelists and forbidden licenses
ALLOWED_LICENSES: Final[set[str]] = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "CC0-1.0",
    "Unlicense",
}

FORBIDDEN_LICENSES: Final[set[str]] = {
    "AGPL-1.0",
    "AGPL-3.0",
    "GPL-1.0",
    "GPL-2.0",
    "GPL-3.0",
    "SSPL-1.0",
    "Commons-Clause",
}

# Semantic Ollama LLM integration defaults
DEFAULT_OLLAMA_URL: Final[str] = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL: Final[str] = "qwen2.5-coder:7b"
FALLBACK_OLLAMA_MODEL: Final[str] = "gemma2:9b"
