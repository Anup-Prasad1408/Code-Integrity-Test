from engines.ast_engine import analyze as ast_analyze, compare_analyses
from engines.stylometry_engine import analyze as style_analyze
from analyzers.risk_engine import calculate_risk

def test_python_ast_valid_and_counts():
    result = ast_analyze("def add(a, b):\n    for x in [a, b]:\n        print(x)\n    return a + b\n", "Python")
    assert result["syntax_valid"] is True
    assert result["functions"] == 1
    assert result["loops"] == 1
    assert result["node_count"] > 0

def test_python_ast_syntax_error():
    result = ast_analyze("def broken(:\n  pass", "Python")
    assert result["syntax_valid"] is False
    assert result["parse_error"]

def test_renamed_python_code_has_structural_overlap():
    a = ast_analyze("def calc_sum(arr):\n total=0\n for x in arr:\n  total += x\n return total\n", "Python")
    b = ast_analyze("def compute(items):\n s=0\n for el in items:\n  s += el\n return s\n", "Python")
    comparison = compare_analyses(a,b)
    assert comparison["comparable"]
    assert comparison["similarity"] > 65

def test_different_languages_not_compared():
    a = ast_analyze("print('hi')", "Python")
    b = ast_analyze("int main(){return 0;}", "C")
    assert compare_analyses(a,b)["comparable"] is False

def test_stylometry_returns_explainable_features():
    result = style_analyze("def f(x):\n    y = x + 1\n    return y\n", "Python")
    assert 0 <= result["stylometry_score"] <= 100
    assert "normalized_entropy" in result["features"]
    assert result["signals"]

def test_risk_score_is_bounded():
    result = calculate_risk({"max_similarity": 90, "stylometry_score": 60, "syntax_valid": True})
    assert 0 <= result["review_score"] <= 100
    assert "not a finding" in result["disclaimer"]
