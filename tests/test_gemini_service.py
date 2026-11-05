"""Unit tests for Gemini configuration and client creation (no live API calls)."""

import pytest

from services import gemini_service
from services.gemini_service import GeminiConfigurationError


def test_client_requires_api_key(monkeypatch):
    monkeypatch.setattr(gemini_service, "get_gemini_api_key", lambda: "")

    with pytest.raises(GeminiConfigurationError, match="Gemini API key is missing"):
        gemini_service.create_gemini_client()


def test_client_uses_explicit_api_key(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, api_key):
            captured["api_key"] = api_key

    monkeypatch.setattr(gemini_service.genai, "Client", FakeClient)
    client = gemini_service.create_gemini_client("  test-key-123  ")

    assert isinstance(client, FakeClient)
    assert captured["api_key"] == "test-key-123"


def test_client_uses_environment_key(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, api_key):
            captured["api_key"] = api_key

    monkeypatch.setattr(gemini_service.genai, "Client", FakeClient)
    monkeypatch.setattr(gemini_service, "get_gemini_api_key", lambda: "env-key-456")

    gemini_service.create_gemini_client()

    assert captured["api_key"] == "env-key-456"
