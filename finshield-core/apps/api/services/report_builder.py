from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io


def build_compliance_report(case: dict, entity: dict, agent_runs: list[dict], risk_assessment: dict | None) -> bytes:
    """
    Builds a PDF compliance report summarizing a case's full audit trail.
    Returns the PDF as raw bytes, ready to stream back as an HTTP response.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=18)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], spaceBefore=16, spaceAfter=6)
    body_style = styles["BodyText"]
    small_style = ParagraphStyle("SmallStyle", parent=styles["BodyText"], fontSize=8, textColor=colors.grey)

    elements = []

    # Header
    elements.append(Paragraph("FinShield Core — Compliance Report", title_style))
    elements.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} &nbsp;|&nbsp; Case ID: {case['id']}",
        small_style
    ))
    elements.append(Spacer(1, 0.2 * inch))

    # Disclaimer — important for an honest compliance-styled artifact
    elements.append(Paragraph(
        "<i>This is an automated, demo-purpose compliance assessment. It is not a "
        "certified regulatory filing and should not be the sole basis for a "
        "financial decision without qualified human review.</i>",
        small_style
    ))
    elements.append(Spacer(1, 0.15 * inch))

    # Entity summary
    elements.append(Paragraph("Entity Summary", heading_style))
    entity_data = [
        ["Name", entity.get("name", "N/A")],
        ["Type", entity.get("entity_type", "N/A")],
        ["Jurisdiction", entity.get("jurisdiction") or "Not provided"],
        ["Case type", case.get("case_type", "N/A")],
    ]
    table = Table(entity_data, colWidths=[1.5 * inch, 4.5 * inch])
    table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.15 * inch))

    # Final risk assessment
    if risk_assessment:
        elements.append(Paragraph("Final Risk Assessment", heading_style))
        elements.append(Paragraph(
            f"<b>Score:</b> {risk_assessment['score']} &nbsp;|&nbsp; "
            f"<b>Band:</b> {risk_assessment['band'].upper()}",
            body_style
        ))
        elements.append(Spacer(1, 0.08 * inch))
        elements.append(Paragraph(f"<b>Rationale:</b> {risk_assessment['rationale']}", body_style))
        elements.append(Spacer(1, 0.15 * inch))

    # Agent-by-agent audit trail
    elements.append(Paragraph("Agent Audit Trail", heading_style))
    for run in agent_runs:
        elements.append(Paragraph(f"<b>{run['agent_name']}</b> — {run['status']}", body_style))
        output = run.get("output") or {}
        summary = output.get("summary", "No summary recorded")
        elements.append(Paragraph(summary, body_style))
        if "confidence" in output:
            elements.append(Paragraph(f"<i>Confidence: {output['confidence']}</i>", small_style))
        elements.append(Spacer(1, 0.1 * inch))

    doc.build(elements)
    return buffer.getvalue()