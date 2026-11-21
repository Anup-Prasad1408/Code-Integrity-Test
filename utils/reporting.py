from io import BytesIO
from datetime import datetime, timezone

def build_pdf_report(records: list[dict], results: dict, comparisons: list[dict]) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    except ImportError as exc:
        raise RuntimeError("PDF reports require reportlab. Install requirements.txt.") from exc

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallCIA", parent=styles["BodyText"], fontSize=8, leading=11))
    story = [
        Paragraph("Student Code Integrity Auditor", styles["Title"]),
        Paragraph("Faculty review report · generated " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), styles["SmallCIA"]),
        Spacer(1, 8*mm),
        Paragraph("Important interpretation", styles["Heading2"]),
        Paragraph("This report contains static-analysis evidence and heuristic indicators. Similarity does not by itself prove plagiarism. Stylometric signals cannot reliably establish AI authorship. Human review and student context are required.", styles["BodyText"]),
        Spacer(1, 5*mm),
        Paragraph("Submission summary", styles["Heading2"]),
    ]
    rows = [["File", "Language", "Lines", "AST status", "Style signal", "Review score"]]
    for rec in records:
        res = results.get(rec["id"], {})
        ast_data = res.get("ast", {})
        style_data = res.get("stylometry", {})
        risk = res.get("risk", {})
        rows.append([
            rec["name"][:28], rec["language"], str(rec["line_count"]),
            ast_data.get("parse_status", "Not run")[:18],
            str(style_data.get("stylometry_score", "—")),
            str(risk.get("review_score", "—")),
        ])
    table = Table(rows, repeatRows=1, colWidths=[48*mm, 22*mm, 13*mm, 36*mm, 24*mm, 25*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#20252b")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),.35,colors.HexColor("#c9ced4")),
        ("FONTSIZE",(0,0),(-1,-1),7), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f3f5f7")]),
        ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    story += [table, Spacer(1, 6*mm), Paragraph("Per-file findings", styles["Heading2"])]
    for rec in records:
        res = results.get(rec["id"])
        if not res:
            continue
        story.append(Paragraph(rec["name"], styles["Heading3"]))
        ast_data = res.get("ast", {})
        style_data = res.get("stylometry", {})
        risk = res.get("risk", {})
        llm = res.get("llm", {})
        story.append(Paragraph(
            f"Parser: {ast_data.get('parse_status','—')} · Syntax valid: {ast_data.get('syntax_valid','—')} · "
            f"Functions: {ast_data.get('functions',0)} · Loops: {ast_data.get('loops',0)} · "
            f"Branches: {ast_data.get('branches',0)}",
            styles["SmallCIA"]))
        story.append(Paragraph(
            f"Stylometry indicator: {style_data.get('stylometry_score','—')}/100 ({style_data.get('band','—')}). "
            + "Signals: " + "; ".join(style_data.get("signals", [])),
            styles["SmallCIA"]))
        story.append(Paragraph(
            f"Review priority: {risk.get('review_score','—')} ({risk.get('band','—')}). "
            f"LLM review: {llm.get('status','not run')}.",
            styles["SmallCIA"]))
        if ast_data.get("parse_error"):
            story.append(Paragraph("Parser note: " + ast_data["parse_error"], styles["SmallCIA"]))
        if llm.get("summary"):
            story.append(Paragraph("LLM summary: " + str(llm["summary"]), styles["SmallCIA"]))
        story.append(Spacer(1, 3*mm))
    if comparisons:
        story.append(Paragraph("Cross-submission structural comparisons", styles["Heading2"]))
        comp_rows = [["File A", "File B", "Similarity", "Interpretation"]]
        for c in comparisons:
            comp_rows.append([c["file_a"][:24], c["file_b"][:24], f'{c["similarity"]}%', c["interpretation"][:45]])
        comp_table = Table(comp_rows, repeatRows=1, colWidths=[42*mm,42*mm,22*mm,62*mm])
        comp_table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#20252b")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),.35,colors.HexColor("#c9ced4")),("FONTSIZE",(0,0),(-1,-1),7),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f3f5f7")]),
        ]))
        story.append(comp_table)
    doc.build(story)
    return buffer.getvalue()
