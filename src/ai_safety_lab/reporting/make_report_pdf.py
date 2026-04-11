from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from ai_safety_lab.reporting.presentation import final_assessment_view, reviewer_panel_view
from ai_safety_lab.schemas import FinalJudgeOutput, JudgeOutput, SystemCase
from ai_safety_lab.settings import AppConfig


def generate_report_pdf(
    output_path: Path,
    system_case: SystemCase,
    judge_outputs: list[JudgeOutput],
    final_output: FinalJudgeOutput,
    settings: AppConfig,
) -> None:
    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    subheading_style = styles["Heading3"]
    body_style = styles["BodyText"]
    body_style.leading = 14
    bullet_style = ParagraphStyle(
        "BulletBody",
        parent=body_style,
        leftIndent=16,
        bulletIndent=0,
        spaceBefore=2,
        spaceAfter=2,
    )
    muted_style = ParagraphStyle(
        "MutedBody",
        parent=body_style,
        textColor=colors.HexColor("#4f6882"),
    )

    reviewer_views = [reviewer_panel_view(judge) for judge in judge_outputs]
    final_view = final_assessment_view(final_output, judge_outputs)

    def add_line(text: str, style: str = "BodyText") -> None:
        story.append(Paragraph(text, styles[style]))
        story.append(Spacer(1, 8))

    def add_paragraph(text: str, style: ParagraphStyle = body_style) -> None:
        story.append(Paragraph(text, style))
        story.append(Spacer(1, 8))

    def add_heading(text: str, style: ParagraphStyle = heading_style) -> None:
        story.append(Paragraph(text, style))
        story.append(Spacer(1, 10))

    def add_bullets(items: list[str], empty_text: str = "None noted.") -> None:
        bullet_items = items or [empty_text]
        for item in bullet_items:
            story.append(Paragraph(item, bullet_style, bulletText="•"))
        story.append(Spacer(1, 8))

    model_summary = ", ".join(system_case.capability_profile.model_backends) or "Unknown"
    # Page 1 - Executive Summary
    add_paragraph("AI Safety Lab Evaluation Report", title_style)
    add_paragraph("Executive Summary", heading_style)
    add_paragraph(f"System / Case ID: {system_case.case_id}")
    add_paragraph(f"Source Type: {system_case.target_type.title()}")
    add_paragraph(f"System Name: {system_case.title}")
    add_paragraph(f"Target Models / Backends: {model_summary}")
    add_paragraph(f"Created At: {system_case.created_at.isoformat()}", muted_style)
    if system_case.source_url:
        add_paragraph(f"Source URL: {system_case.source_url}", muted_style)

    add_heading("Final Assessment", subheading_style)
    add_paragraph(f"Verdict: {final_view['verdict']}")
    add_paragraph(f"Risk Level: {final_view['risk_level']}")
    add_paragraph(f"Confidence: {final_view['confidence']}")
    add_paragraph(f"Recommendation: {final_view['recommendation']}")

    add_heading("Top Risks", subheading_style)
    unique_risks: list[str] = []
    for judge in judge_outputs:
        for risk in judge.top_3_risks:
            if risk not in unique_risks:
                unique_risks.append(risk)
    add_bullets(unique_risks[:5], empty_text="No top risks were identified.")

    add_heading("Why This Decision Was Made", subheading_style)
    add_bullets(list(final_view["reasons"]), empty_text="No concise decision reasons were available.")

    if system_case.derived_observations.detected_risk_surfaces:
        add_heading("Detected Risk Surfaces", subheading_style)
        add_bullets(system_case.derived_observations.detected_risk_surfaces)
    if system_case.derived_observations.open_questions:
        add_heading("Open Questions", subheading_style)
        add_bullets(system_case.derived_observations.open_questions)

    # Page 2 - Key Findings
    story.append(PageBreak())
    add_paragraph("Key Findings", heading_style)
    for index, reason in enumerate(list(final_view["reasons"])[:5], start=1):
        add_heading(f"Finding {index}", subheading_style)
        add_paragraph(reason)

    # Page 3 - Reviewer Alignment
    story.append(PageBreak())
    add_paragraph("Reviewer Alignment", heading_style)
    alignment = final_view["alignment"]
    add_paragraph(f"Alignment Status: {alignment['label']}")
    add_paragraph(str(alignment["summary"]))
    add_heading("Observed Differences", subheading_style)
    add_bullets(list(alignment["details"]), empty_text="No material differences were recorded.")

    # Page 4+ - Reviewer Breakdown
    story.append(PageBreak())
    add_paragraph("Expert Reviewer Breakdown", heading_style)
    for view in reviewer_views:
        add_heading(str(view["label"]), subheading_style)
        add_paragraph(
            f"Verdict: {view['verdict']} | Risk Score: {view['risk_score']} | Confidence: {view['confidence']}"
        )
        add_paragraph(f"Risk Level: {view['risk_level']}")
        add_heading("Key Risks", styles["Heading4"])
        add_bullets(list(view["key_risks"]), empty_text="No key risks were provided.")
        add_heading("Recommendations", styles["Heading4"])
        add_bullets(list(view["mitigations"]), empty_text="No recommendations were provided.")
        add_paragraph(f"Summary: {view['summary']}")
        add_heading("Category Highlights", styles["Heading4"])
        add_bullets(list(view["category_highlights"]), empty_text="No category highlights were available.")
        story.append(Spacer(1, 10))

    add_heading("Final Assessment", subheading_style)
    add_paragraph(
        f"Verdict: {final_view['verdict']} | Risk Score: {final_view['risk_score']} | Confidence: {final_view['confidence']}"
    )
    add_paragraph(f"Risk Level: {final_view['risk_level']}")
    add_paragraph(f"Recommendation: {final_view['recommendation']}")
    add_heading("Main Reasons", styles["Heading4"])
    add_bullets(list(final_view["main_reasons"]), empty_text="No main reasons were provided.")
    add_paragraph(f"Summary: {final_view['summary']}")

    # Final page - Required Actions
    story.append(PageBreak())
    add_paragraph("Required Actions", heading_style)
    add_bullets(list(final_view["required_actions"]), empty_text="No required actions were specified.")
    add_heading("Deployment Recommendation", subheading_style)
    add_paragraph(final_view["recommendation"])
    add_paragraph(
        "Run Metadata: "
        + ", ".join(f"{key}={value.backend}/{value.model}" for key, value in settings.providers.items()),
        muted_style,
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    document.build(story)
