
from __future__ import annotations

import ast
import hashlib
import re
from collections import Counter
from difflib import SequenceMatcher

from parsers.python_parser import parse_source as parse_python


TOKEN_RE = re.compile(
    r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`|'
    r'[A-Za-z_$][A-Za-z0-9_$]*|(?:\d+(?:\.\d+)?)|'
    r'===|!==|==|!=|<=|>=|=>|\+\+|--|\+=|-=|\*=|/=|&&|\|\||->|::|'
    r'[{}()\[\];,.?:~!%^&*+\-/=<>|]'
)

KEYWORDS = {
    "Python": set(
        "def class if elif else for while try except finally with as return "
        "yield raise import from pass break continue lambda async await "
        "True False None and or not in is global nonlocal match case".split()
    ),
    "JavaScript": set(
        "function class if else for while do switch case break continue return "
        "try catch finally throw new const let var import from export default "
        "async await yield this true false null undefined typeof instanceof "
        "in of".split()
    ),
    "C": set(
        "int char float double void long short signed unsigned const static "
        "struct typedef enum union if else for while do switch case break "
        "continue return sizeof include define NULL".split()
    ),
}

OPERATORS = {
    "==", "!=", "===", "!==", "<", ">", "<=", ">=",
    "+", "-", "*", "/", "%", "=", "+=", "-=", "*=", "/=",
    "&&", "||", "!", "&", "|", "^", "++", "--"
}


def tokenize(source: str, language: str) -> list[str]:
    tokens = TOKEN_RE.findall(source)
    result = []

    for token in tokens:
        if token.startswith(("'", '"', "`")):
            result.append("<STR>")
        elif token[0].isdigit():
            result.append("<NUM>")
        elif re.match(r"[A-Za-z_$]", token):
            if token in KEYWORDS.get(language, set()):
                result.append(token)
            else:
                result.append("<ID>")
        else:
            result.append(token)

    return result


def strip_c_comments(source: str) -> str:
    """Remove C comments while preserving strings and line structure."""

    result = []
    i = 0
    state = "normal"

    while i < len(source):
        char = source[i]
        next_char = source[i + 1] if i + 1 < len(source) else ""

        if state == "normal":
            if char == '"':
                state = "string"
                result.append(char)
                i += 1

            elif char == "'":
                state = "character"
                result.append(char)
                i += 1

            elif char == "/" and next_char == "/":
                state = "line_comment"
                result.extend([" ", " "])
                i += 2

            elif char == "/" and next_char == "*":
                state = "block_comment"
                result.extend([" ", " "])
                i += 2

            else:
                result.append(char)
                i += 1

        elif state in ("string", "character"):
            result.append(char)

            if char == "\\" and i + 1 < len(source):
                result.append(source[i + 1])
                i += 2

            else:
                if state == "string" and char == '"':
                    state = "normal"
                elif state == "character" and char == "'":
                    state = "normal"

                i += 1

        elif state == "line_comment":
            if char == "\n":
                result.append("\n")
                state = "normal"
            else:
                result.append(" ")

            i += 1

        elif state == "block_comment":
            if char == "*" and next_char == "/":
                result.extend([" ", " "])
                state = "normal"
                i += 2

            else:
                result.append("\n" if char == "\n" else " ")
                i += 1

    return "".join(result)


def language_ast_features(source: str, language: str):
    labels = []
    edges = []

    if language == "JavaScript":
        import esprima

        try:
            tree = esprima.parseScript(source)
        except Exception:
            tree = esprima.parseModule(source)

        def walk(node):
            if node is None:
                return

            node_type = getattr(node, "type", None)

            if not isinstance(node_type, str):
                return

            labels.append(node_type)

            ignored = {"type", "loc", "range", "tokens", "comments"}

            for key, value in vars(node).items():
                if key in ignored:
                    continue

                children = value if isinstance(value, list) else [value]

                for child in children:
                    child_type = getattr(child, "type", None)

                    if isinstance(child_type, str):
                        edges.append(f"{node_type}>{child_type}")
                        walk(child)

        walk(tree)
        return labels, edges

    elif language == "C":
        import re
        from pycparser import c_parser, c_ast

        cleaned_source = strip_c_comments(source)

        cleaned_source = re.sub(
            r"(?m)^\s*#.*$",
            "",
            cleaned_source
        )

        tree = c_parser.CParser().parse(cleaned_source)

        def walk(node):
            if not isinstance(node, c_ast.Node):
                return

            node_type = type(node).__name__
            labels.append(node_type)

            for _, child in node.children():
                child_type = type(child).__name__
                edges.append(f"{node_type}>{child_type}")
                walk(child)

        walk(tree)
        return labels, edges

    else:
        raise ValueError(f"Unsupported language: {language}")



def python_features(source: str):
    tree = parse_python(source)

    labels = []
    edges = []

    def walk(node):
        if not isinstance(node, ast.AST):
            return

        labels.append(type(node).__name__)

        for _, value in ast.iter_fields(node):
            children = value if isinstance(value, list) else [value]

            for child in children:
                if isinstance(child, ast.AST):
                    edges.append(
                        f"{type(node).__name__}>{type(child).__name__}"
                    )
                    walk(child)

    walk(tree)

    functions = sum(
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        for n in ast.walk(tree)
    )
    classes = sum(
        isinstance(n, ast.ClassDef) for n in ast.walk(tree)
    )
    branches = sum(
        isinstance(n, (ast.If, ast.IfExp, ast.Match))
        for n in ast.walk(tree)
    )
    loops = sum(
        isinstance(n, (ast.For, ast.AsyncFor, ast.While))
        for n in ast.walk(tree)
    )

    return labels, edges, functions, classes, branches, loops


def make_ngrams(items: list[str], size: int) -> Counter:
    if len(items) < size:
        return Counter()

    return Counter(
        tuple(items[i:i + size])
        for i in range(len(items) - size + 1)
    )


def counter_similarity(a: Counter, b: Counter) -> float:
    """Multiset Jaccard similarity."""
    if not a or not b:
        return 0.0

    keys = set(a) | set(b)

    intersection = sum(min(a[k], b[k]) for k in keys)
    union = sum(max(a[k], b[k]) for k in keys)

    return intersection / union if union else 0.0


def distribution_similarity(a: Counter, b: Counter) -> float:
    """Compare relative feature frequencies."""
    if not a or not b:
        return 0.0

    total_a = sum(a.values())
    total_b = sum(b.values())

    keys = set(a) | set(b)

    distance = sum(
        abs((a[k] / total_a) - (b[k] / total_b))
        for k in keys
    )

    return max(0.0, 1.0 - distance / 2.0)


def analyze(source_code: str, language: str) -> dict:
    result = {
        "language": language,
        "parse_status": "lexical fallback",
        "syntax_valid": True,
        "node_count": 0,
        "structural_fingerprint": "",
        "normalized_tokens": [],
        "functions": 0,
        "classes": 0,
        "branches": 0,
        "loops": 0,
        "structure": [],
        "parse_error": None,
        "structural_ngrams": {},
        "edge_features": {},
        "token_ngrams": {},
        "operator_features": {},
    }

    if not source_code.strip():
        result.update(
            syntax_valid=False,
            parse_status="empty",
            parse_error="No source code provided."
        )
        return result

    labels = []
    edges = []

    try:
        if language == "Python":
            (
                labels,
                edges,
                result["functions"],
                result["classes"],
                result["branches"],
                result["loops"],
            ) = python_features(source_code)

            result["parse_status"] = "native Python AST"

        else:
            try:
                labels, edges = language_ast_features(
                    source_code, language
                )

                result["parse_status"] = (
                    "Esprima AST" if language == "JavaScript"
                    else "pycparser AST"
                )

                result["syntax_valid"] = True


                toks = tokenize(source_code, language)

                result["functions"] = sum(
                    1 for i, token in enumerate(toks[:-1])
                    if token == "<ID>" and toks[i + 1] == "("
                )
                result["classes"] = sum(
                    1 for token in toks if token == "class"
                )
                result["branches"] = sum(
                    1 for token in toks
                    if token in {"if", "switch", "case", "?"}
                )
                result["loops"] = sum(
                    1 for token in toks
                    if token in {"for", "while", "do"}
                )

            except (ImportError, ModuleNotFoundError):
                labels = tokenize(source_code, language)
                result["parse_status"] = (
                    "token fallback (Tree-sitter unavailable)"
                )

            except Exception as exc:
                import traceback

                print("\n===== PARSER DEBUG ERROR =====")
                traceback.print_exc()
                print("===== END PARSER DEBUG =====\n")

                labels = tokenize(source_code, language)
                result["parse_status"] = "token fallback"
                result["parse_error"] = f"{type(exc).__name__}: {exc!s}"

                result["syntax_valid"] = False

    except SyntaxError as exc:
        labels = tokenize(source_code, language)
        result["syntax_valid"] = False
        result["parse_status"] = "syntax error"
        result["parse_error"] = (
            f"Line {exc.lineno or '?'}: {exc.msg}"
        )

    except Exception as exc:
        labels = tokenize(source_code, language)
        result["syntax_valid"] = False
        result["parse_status"] = "parser error"
        result["parse_error"] = (
            f"{type(exc).__name__}: {exc}"
        )

    normalized = tokenize(source_code, language)

    result["normalized_tokens"] = normalized[:20000]
    result["structure"] = labels[:5000]
    result["node_count"] = len(labels)

    structural_ngrams = make_ngrams(labels, 3)
    token_ngrams = make_ngrams(normalized, 4)
    edge_features = Counter(edges)
    operator_features = Counter(
        token for token in normalized if token in OPERATORS
    )

    result["structural_ngrams"] = {
        repr(k): v for k, v in structural_ngrams.items()
    }
    result["edge_features"] = dict(edge_features)
    result["token_ngrams"] = {
        repr(k): v for k, v in token_ngrams.items()
    }
    result["operator_features"] = dict(operator_features)

    fingerprint_source = "|".join(labels)

    result["structural_fingerprint"] = hashlib.sha256(
        fingerprint_source.encode("utf-8")
    ).hexdigest()

    return result


def compare_analyses(a: dict, b: dict) -> dict:
    if a.get("language") != b.get("language"):
        return {
            "comparable": False,
            "similarity": None,
            "reason": "Different programming languages."
        }

    seq_a = a.get("structure", [])
    seq_b = b.get("structure", [])

    tok_a = a.get("normalized_tokens", [])
    tok_b = b.get("normalized_tokens", [])

    if not seq_a or not seq_b or not tok_a or not tok_b:
        return {
            "comparable": False,
            "similarity": None,
            "reason": "One submission has no comparable structure."
        }

    # Rebuild feature counters from stored analysis data.
    structural_a = Counter(a.get("structural_ngrams", {}))
    structural_b = Counter(b.get("structural_ngrams", {}))

    edges_a = Counter(a.get("edge_features", {}))
    edges_b = Counter(b.get("edge_features", {}))

    tokens_a = Counter(a.get("token_ngrams", {}))
    tokens_b = Counter(b.get("token_ngrams", {}))

    operators_a = Counter(a.get("operator_features", {}))
    operators_b = Counter(b.get("operator_features", {}))

    structure_score = counter_similarity(
        structural_a, structural_b
    )

    edge_score = counter_similarity(edges_a, edges_b)

    token_score = counter_similarity(
        tokens_a, tokens_b
    )

    operator_score = distribution_similarity(
        operators_a, operators_b
    )

    # Sequence matching is retained as a small supporting signal.
    sequence_score = SequenceMatcher(
        None, seq_a, seq_b, autojunk=False
    ).ratio()

    # Weighted score: structural relationships and patterns matter
    # more than generic token or sequence overlap.
    score = (
        0.30 * structure_score
        + 0.30 * edge_score
        + 0.20 * token_score
        + 0.10 * operator_score
        + 0.10 * sequence_score
    ) * 100

    exact = (
        a.get("structural_fingerprint")
        == b.get("structural_fingerprint")
    )

    if score >= 80:
        interpretation = (
            "High structural overlap; manual review recommended."
        )
    elif score >= 60:
        interpretation = (
            "Moderate structural overlap; inspect matching patterns."
        )
    else:
        interpretation = (
            "Lower structural overlap in this comparison."
        )

    return {
        "comparable": True,
        "similarity": round(score, 1),
        "structure_similarity": round(structure_score * 100, 1),
        "edge_similarity": round(edge_score * 100, 1),
        "normalized_token_similarity": round(token_score * 100, 1),
        "operator_similarity": round(operator_score * 100, 1),
        "sequence_similarity": round(sequence_score * 100, 1),
        "exact_structural_fingerprint": exact,
        "interpretation": interpretation,
    }


class ASTEngine:
    def analyze(self, source_code: str, language: str):
        return analyze(source_code, language)
