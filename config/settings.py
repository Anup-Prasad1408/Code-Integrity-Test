"""Centralized environment configuration for Code Integrity Auditor."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load local variables without overriding variables already provided by the host.
load_dotenv(dotenv_path=ENV_FILE, override=False)

DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"


def get_gemini_api_key() -> str:
    """Return the configured Gemini API key, or an empty string if absent."""
    return os.getenv("GEMINI_API_KEY", "").strip()


def get_gemini_model() -> str:
    """Return the configured Gemini model identifier."""
    return os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL
