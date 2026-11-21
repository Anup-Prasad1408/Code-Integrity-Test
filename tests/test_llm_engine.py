from engines.llm_engine import analyze

def test_llm_is_optional_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = analyze("print(1)", "Python", "Print one", provider="gemini")
    assert result["enabled"] is False
    assert result["adherence_score"] is None

def test_llm_requires_requirements(monkeypatch):
    result = analyze("print(1)", "Python", "", api_key="fake-key", provider="openai")
    assert result["status"] == "Requirements missing"
    assert result["enabled"] is True
