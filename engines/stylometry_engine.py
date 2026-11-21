from __future__ import annotations

import math
import re
from collections import Counter

from engines.ast_engine import TOKEN_RE, KEYWORDS

COMMENT_PATTERNS = {
    "Python": re.compile(r"#.*"),
    "JavaScript": re.compile(r"//.*|/\*[\s\S]*?\*/"),
    "C": re.compile(r"//.*|/\*[\s\S]*?\*/"),
}

def _entropy(tokens):
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    total = len(tokens)
    return -sum((n/total) * math.log2(n/total) for n in counts.values())

def analyze(source_code: str, language: str) -> dict:
    lines = source_code.splitlines()
    nonempty = [line for line in lines if line.strip()]
    comment_pattern = COMMENT_PATTERNS.get(language, COMMENT_PATTERNS["C"])
    comments = comment_pattern.findall(source_code)
    code_without_comments = comment_pattern.sub("", source_code)
    tokens = TOKEN_RE.findall(code_without_comments)
    identifiers = [t for t in tokens if re.match(r"^[A-Za-z_$][A-Za-z0-9_$]*$", t)
                   and t not in KEYWORDS.get(language, set())]
    entropy = _entropy(tokens)
    max_entropy = math.log2(max(2, len(set(tokens))))
    normalized_entropy = entropy / max_entropy if max_entropy else 0.0
    lengths = [len(line) for line in nonempty]
    avg_line_length = sum(lengths) / len(lengths) if lengths else 0.0
    long_line_ratio = sum(n > 100 for n in lengths) / len(lengths) if lengths else 0.0
    indent_widths = []
    for line in nonempty:
        prefix = len(line) - len(line.lstrip(" \t"))
        if prefix:
            indent_widths.append(prefix)
    indent_counts = Counter(indent_widths)
    indent_consistency = (max(indent_counts.values()) / len(indent_widths)) if indent_widths else 1.0
    comment_ratio = len(comments) / max(1, len(nonempty))
    identifier_lengths = [len(x) for x in identifiers]
    avg_identifier_length = sum(identifier_lengths) / len(identifier_lengths) if identifier_lengths else 0
    unique_ratio = len(set(tokens)) / max(1, len(tokens))

    # Transparent heuristic indicator, NOT a trained AI-authorship classifier.
    # Smooth, highly repetitive token distributions and extremely uniform formatting
    # can be review signals, but also occur in human-written code.
    entropy_signal = max(0.0, 1.0 - normalized_entropy)
    uniformity_signal = indent_consistency
    sparse_comment_signal = max(0.0, 1.0 - min(comment_ratio / 0.18, 1.0))
    repeated_token_signal = max(0.0, 1.0 - min(unique_ratio / 0.55, 1.0))
    style_score = round(100 * (
        0.34 * entropy_signal + 0.24 * uniformity_signal +
        0.18 * sparse_comment_signal + 0.24 * repeated_token_signal
    ), 1)
    score = max(0.0, min(100.0, style_score))
    if score >= 70:
        band = "Elevated stylometric signal"
    elif score >= 45:
        band = "Moderate stylometric signal"
    else:
        band = "Lower stylometric signal"
    signals = []
    if normalized_entropy < 0.55:
        signals.append("Low normalized token entropy")
    if indent_consistency > 0.9 and len(indent_widths) >= 4:
        signals.append("Highly consistent indentation")
    if comment_ratio < 0.03 and len(nonempty) >= 12:
        signals.append("Very low comment density")
    if unique_ratio < 0.35 and len(tokens) >= 30:
        signals.append("High token repetition")
    if not signals:
        signals.append("No strong stylometric outlier among the measured features")
    return {
        "stylometry_score": score, "band": band, "signals": signals,
        "features": {
            "token_count": len(tokens), "unique_token_ratio": round(unique_ratio, 3),
            "token_entropy_bits": round(entropy, 3), "normalized_entropy": round(normalized_entropy, 3),
            "comment_to_nonempty_line_ratio": round(comment_ratio, 3),
            "indentation_consistency": round(indent_consistency, 3),
            "average_line_length": round(avg_line_length, 1),
            "long_line_ratio": round(long_line_ratio, 3),
            "average_identifier_length": round(avg_identifier_length, 1),
            "nonempty_lines": len(nonempty),
        },
        "interpretation": "This is a heuristic style-anomaly indicator, not proof that code was written by AI. Human code can show the same patterns.",
    }

class StylometryEngine:
    def analyze(self, source_code: str, language: str):
        return analyze(source_code, language)
