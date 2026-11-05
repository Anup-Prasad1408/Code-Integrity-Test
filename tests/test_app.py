"""Basic Day 1 project smoke tests."""

from config.settings import DEFAULT_GEMINI_MODEL, get_gemini_model


def test_default_gemini_model_is_defined():
    assert DEFAULT_GEMINI_MODEL


def test_gemini_model_falls_back_when_environment_value_is_blank(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "   ")
    assert get_gemini_model() == DEFAULT_GEMINI_MODEL
