"""Small Gemini API integration used by the Day 1 setup dashboard."""

from __future__ import annotations

from google import genai

from config.settings import get_gemini_api_key, get_gemini_model


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini cannot be initialized because configuration is missing."""


def create_gemini_client(api_key: str | None = None) -> genai.Client:
    """Create a Gemini Developer API client using an explicit or environment key."""
    resolved_key = (api_key if api_key is not None else get_gemini_api_key()).strip()
    if not resolved_key:
        raise GeminiConfigurationError(
            "Gemini API key is missing. Copy .env.example to .env and set GEMINI_API_KEY."
        )
    return genai.Client(api_key=resolved_key)


def test_gemini_connection() -> str:
    """Send a minimal test prompt and return Gemini's text response."""
    client = create_gemini_client()
    response = client.models.generate_content(
        model=get_gemini_model(),
        contents="Reply with exactly: Code Integrity Auditor Gemini connection successful.",
    )
    response_text = (response.text or "").strip()
    if not response_text:
        raise RuntimeError("Gemini returned an empty response. Check the model and API access.")
    return response_text
