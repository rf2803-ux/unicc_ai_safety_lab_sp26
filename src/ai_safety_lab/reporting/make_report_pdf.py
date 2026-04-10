from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
    unique_risks: list[str] = []
    for judge in judge_outputs:
        for risk in judge.top_3_risks:
            if risk not in unique_risks:
                unique_risks.append(risk)

    def add_line(text: str, style: str = "BodyText") -> None:
        story.append(Paragraph(text, styles[style]))
        story.append(Spacer(1, 8))

    model_summary = ", ".join(system_case.capability_profile.model_backends) or "Unknown"
    add_line("AI Safety Lab Report", "Title")
    add_line(f"Case ID: {system_case.case_id}")
    add_line(f"Target Type: {system_case.target_type}")
    add_line(f"Target Label: {system_case.title}")
    add_line(f"Target Models/Backends: {model_summary}")
    add_line(f"Created At: {system_case.created_at.isoformat()}")
    if system_case.source_url:
        add_line(f"Source URL: {system_case.source_url}")
    add_line(
        f"Executive Summary: Final verdict {final_output.final_verdict} with score {final_output.final_score}. "
        f"Required actions: {', '.join(final_output.required_actions) or 'None'}"
    )
    add_line(f"Top Risks: {', '.join(unique_risks[:3]) or 'None identified'}")
    if system_case.derived_observations.detected_risk_surfaces:
        add_line(
            f"Detected Risk Surfaces: {', '.join(system_case.derived_observations.detected_risk_surfaces)}"
        )
    if system_case.derived_observations.open_questions:
        add_line(f"Open Questions: {', '.join(system_case.derived_observations.open_questions)}")

    for judge in judge_outputs:
        add_line(f"{judge.judge_id.upper()} Summary", "Heading2")
        add_line(f"Verdict: {judge.overall_verdict} | Score: {judge.overall_score} | Confidence: {judge.confidence}")
        add_line(f"Summary: {judge.summary or 'No summary provided.'}")
        for category, details in judge.category_scores.items():
            evidence = "; ".join(details.evidence_snippets) or "No evidence snippets provided."
            add_line(
                f"{category}: score {details.score}. Rationale: {details.rationale}. Evidence: {evidence}"
            )

    add_line("Ultimate Judge", "Heading2")
    add_line(f"Verdict: {final_output.final_verdict} | Score: {final_output.final_score} | Confidence: {final_output.confidence}")
    add_line(f"Agreement Summary: {'; '.join(f'{item.judge_id}: {item.verdict}' for item in final_output.agreement_summary)}")
    add_line(f"Key Conflicts: {', '.join(final_output.key_conflicts) or 'None'}")
    add_line(f"Final Rationale: {final_output.final_rationale}")
    add_line(f"Required Actions: {', '.join(final_output.required_actions) or 'None'}")
    add_line(
        "Run Metadata: "
        + ", ".join(f"{key}={value.backend}/{value.model}" for key, value in settings.providers.items())
    )

    document = SimpleDocTemplate(str(output_path), pagesize=letter)
    document.build(story)
