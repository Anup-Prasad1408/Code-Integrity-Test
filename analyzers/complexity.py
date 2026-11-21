import ast
import re

def analyze_complexity(source_code: str, language: str) -> dict:
    if language == "Python":
        try:
            tree = ast.parse(source_code)
            branches = sum(isinstance(n, (ast.If, ast.IfExp, ast.Match, ast.ExceptHandler)) for n in ast.walk(tree))
            loops = sum(isinstance(n, (ast.For, ast.AsyncFor, ast.While)) for n in ast.walk(tree))
            functions = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
            classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
            return {"branches": branches, "loops": loops, "functions": functions, "classes": classes,
                    "estimated_complexity": 1 + branches + loops, "method": "Python AST"}
        except SyntaxError:
            pass
    tokens = re.findall(r"\b(if|else|for|while|case|catch|switch)\b|\b(function)\b", source_code)
    branches = sum(1 for x in re.findall(r"\b(if|else|case|catch|switch)\b", source_code))
    loops = sum(1 for x in re.findall(r"\b(for|while)\b", source_code))
    functions = len(re.findall(r"\bfunction\b|\b[A-Za-z_$]\w*\s*\([^;{}]*\)\s*\{", source_code))
    classes = len(re.findall(r"\bclass\s+\w+", source_code))
    return {"branches": branches, "loops": loops, "functions": functions, "classes": classes,
            "estimated_complexity": 1 + branches + loops, "method": "lexical estimate"}

