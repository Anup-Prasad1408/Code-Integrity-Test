def calculate_risk(signals: dict) -> dict:
    """Aggregate measurable evidence; do not label a person or assert misconduct."""
    similarity = signals.get("max_similarity")
    style = signals.get("stylometry_score")
    syntax_valid = signals.get("syntax_valid", True)
    components = []
    if similarity is not None:
        components.append(("structural similarity", float(similarity), 0.65))
    if style is not None:
        components.append(("stylometric anomaly", float(style), 0.35))
    if not components:
        score = None
    else:
        weight = sum(item[2] for item in components)
        score = round(sum(v*w for _,v,w in components)/weight, 1)
    if score is None:
        band = "Insufficient evidence"
    elif score >= 75:
        band = "High review priority"
    elif score >= 50:
        band = "Needs manual review"
    else:
        band = "Lower review priority"
    notes = [f"{name}: {value:.1f}/100" for name,value,_ in components]
    if syntax_valid is False:
        notes.append("Syntax/parser issue detected; structural results may be incomplete.")
    return {"review_score": score, "band": band, "evidence": notes,
            "disclaimer": "A review-priority score is not a finding of guilt, plagiarism, or AI authorship."}
