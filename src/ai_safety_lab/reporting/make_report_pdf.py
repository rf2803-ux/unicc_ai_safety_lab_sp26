from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ai_safety_lab.reporting.presentation import (
    CATEGORY_LABELS,
    final_assessment_view,
    reviewer_panel_view,
)
from ai_safety_lab.schemas import FinalJudgeOutput, JudgeOutput, SystemCase
from ai_safety_lab.settings import AppConfig


BG_SOFT = colors.HexColor("#F6F2EA")
BG_LIGHT_RED = colors.HexColor("#FCECEC")
BG_LIGHT_GOLD = colors.HexColor("#FBF1D8")
TEXT_DARK = colors.HexColor("#2F3136")
TEXT_MUTED = colors.HexColor("#8B8A83")
BORDER = colors.HexColor("#D9D4CA")
RED = colors.HexColor("#E94A4A")
GOLD = colors.HexColor("#C88012")
BLUE = colors.HexColor("#1E67B2")
CARD_WHITE = colors.white
TEAL = colors.HexColor("#0F6E56")
PAGE_BG = colors.HexColor("#F7F6F3")

VERDICT_COLORS = {
    "Safe": TEAL,
    "Needs Review": GOLD,
    "Unsafe": RED,
}

RISK_ROW_COLORS = {
    "Auditability": BLUE,
    "Privacy": GOLD,
    "Bias / Fairness": GOLD,
    "Harmful Content": RED,
    "Security": RED,
    "Prompt Injection": RED,
    "Transparency": BLUE,
    "Deception": RED,
}

CONTROL_STATUS_COLORS = {
    "Needs attention": GOLD,
    "Review needed": BLUE,
    "Better supported": TEAL,
}

CONTROL_STATUS_BACKGROUNDS = {
    "Needs attention": BG_LIGHT_GOLD,
    "Review needed": colors.HexColor("#EAF4FD"),
    "Better supported": colors.HexColor("#EAF7EF"),
}


def _html_color(color: colors.Color) -> str:
    return f"#{int(color.red * 255):02X}{int(color.green * 255):02X}{int(color.blue * 255):02X}"


def _page_chrome(canvas, doc) -> None:
    canvas.saveState()
    page_width, page_height = A4
    margin = 10 * mm
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.roundRect(margin, margin, page_width - (2 * margin), page_height - (2 * margin), 6, stroke=1, fill=0)
    canvas.setLineWidth(0.4)
    canvas.setStrokeColor(BORDER)
    canvas.line(margin + 4, margin + 6 * mm, page_width - margin - 4, margin + 6 * mm)
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawCentredString(page_width / 2, margin + 2.5 * mm, f"AI Safety Lab · Evaluation Report · Page {doc.page}")
    canvas.restoreState()


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "eyebrow": ParagraphStyle(
            "eyebrow",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=TEXT_MUTED,
            leading=10,
        ),
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=TEXT_DARK,
            spaceAfter=6,
        ),
        "section": ParagraphStyle(
            "section",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=18,
            textColor=TEXT_DARK,
            spaceAfter=8,
        ),
        "small_label": ParagraphStyle(
            "small_label",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=10,
            textColor=TEXT_MUTED,
            uppercase=True,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=TEXT_DARK,
            alignment=TA_LEFT,
        ),
        "body_small": ParagraphStyle(
            "body_small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=TEXT_DARK,
        ),
        "body_muted": ParagraphStyle(
            "body_muted",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=TEXT_MUTED,
        ),
        "body_muted_dark": ParagraphStyle(
            "body_muted_dark",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=TEXT_DARK,
        ),
        "reviewer_name": ParagraphStyle(
            "reviewer_name",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=TEXT_DARK,
        ),
        "subhead": ParagraphStyle(
            "subhead",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=TEXT_MUTED,
        ),
        "mono": ParagraphStyle(
            "mono",
            parent=base["Normal"],
            fontName="Courier",
            fontSize=7,
            leading=10,
            textColor=TEXT_MUTED,
        ),
        "metric": ParagraphStyle(
            "metric",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=TEXT_DARK,
        ),
        "metric_red": ParagraphStyle(
            "metric_red",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=RED,
        ),
        "metric_gold": ParagraphStyle(
            "metric_gold",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=GOLD,
        ),
        "metric_blue": ParagraphStyle(
            "metric_blue",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=BLUE,
        ),
        "metric_teal": ParagraphStyle(
            "metric_teal",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=TEAL,
        ),
        "metric_compact": ParagraphStyle(
            "metric_compact",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=TEXT_DARK,
        ),
        "metric_compact_red": ParagraphStyle(
            "metric_compact_red",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=RED,
        ),
        "metric_compact_gold": ParagraphStyle(
            "metric_compact_gold",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=GOLD,
        ),
        "metric_compact_blue": ParagraphStyle(
            "metric_compact_blue",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=BLUE,
        ),
        "risk_level_red": ParagraphStyle(
            "risk_level_red",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=RED,
        ),
        "risk_level_gold": ParagraphStyle(
            "risk_level_gold",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=GOLD,
        ),
        "risk_level_teal": ParagraphStyle(
            "risk_level_teal",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=TEAL,
        ),
        "recommendation_metric": ParagraphStyle(
            "recommendation_metric",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=RED,
        ),
        "badge_title": ParagraphStyle(
            "badge_title",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=16,
            textColor=colors.white,
        ),
        "badge_body": ParagraphStyle(
            "badge_body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.white,
        ),
    }


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph((text or "").replace("\n", "<br/>"), style)


def _source_type_label(system_case: SystemCase) -> str:
    mapping = {
        "repository": "Repository (GitHub)",
        "endpoint": "Runtime (App / Endpoint URL)",
        "conversation": "JSON / Generated Case",
    }
    return mapping.get(system_case.target_type, system_case.target_type.title())


def _targets_label(system_case: SystemCase) -> str:
    targets = system_case.capability_profile.model_backends
    if not targets:
        return "unknown"
    return " · ".join(targets[:3])


def _reviewer_rows(judge_outputs: list[JudgeOutput]) -> list[dict[str, object]]:
    return [reviewer_panel_view(judge) for judge in judge_outputs]


def _top_risks(judge_outputs: list[JudgeOutput]) -> list[tuple[str, str]]:
    category_data: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for judge in judge_outputs:
        for category, details in judge.category_scores.items():
            category_data[category].append((details.score, details.rationale))

    ranked: list[tuple[float, str, str]] = []
    for category, entries in category_data.items():
        avg_score = sum(score for score, _ in entries) / len(entries)
        best_rationale = sorted(entries, key=lambda item: item[0])[0][1]
        label = CATEGORY_LABELS.get(category, category.replace("_", " ").title())
        ranked.append((avg_score, label, best_rationale))

    ranked.sort(key=lambda item: item[0])
    return [(label, rationale) for _, label, rationale in ranked[:5]]


def _action_label(text: str, index: int) -> str:
    lowered = text.lower()
    mapping = [
        ("training", "Training data"),
        ("retrain", "Training data"),
        ("upload", "File security"),
        ("sandbox", "File security"),
        ("prompt injection", "Prompt injection"),
        ("sanitize", "Prompt injection"),
        ("audit", "Auditability"),
        ("logging", "Auditability"),
        ("transparency", "Transparency"),
        ("disclaimer", "Transparency"),
        ("human", "Human review"),
        ("review", "Human review"),
    ]
    for needle, label in mapping:
        if needle in lowered:
            return label
    return f"Action {index}"


def _metadata_footer(settings: AppConfig) -> str:
    parts = []
    for provider_id in ("judge1", "judge2", "judge3", "ultimate_judge"):
        provider = settings.providers.get(provider_id)
        if provider:
            parts.append(f"{provider_id}={provider.backend}/{provider.model}")
    return " · ".join(parts)


def _table(data: list[list[object]], widths: list[float], style_commands: list[tuple]) -> Table:
    table = Table(data, colWidths=widths, hAlign="LEFT")
    table.setStyle(TableStyle(style_commands))
    return table


def _risk_level_style(value: str, styles: dict[str, ParagraphStyle]) -> ParagraphStyle:
    mapping = {
        "High": "risk_level_red",
        "Medium": "risk_level_gold",
        "Low": "risk_level_teal",
        "Safe": "risk_level_teal",
        "Needs Review": "risk_level_gold",
        "Unsafe": "risk_level_red",
    }
    return styles.get(mapping.get(value, "risk_level_gold"), styles["risk_level_gold"])


def _cover_header(story: list[object], styles: dict[str, ParagraphStyle], final_view: dict[str, object]) -> None:
    verdict = str(final_view["verdict"])
    recommendation = str(final_view["recommendation"])
    badge = _table(
        [
            [_p(verdict.upper(), styles["badge_title"])],
            [_p(recommendation.replace(" until critical issues are addressed", ""), styles["badge_body"])],
        ],
        [62 * mm],
        [
            ("BACKGROUND", (0, 0), (-1, -1), VERDICT_COLORS.get(verdict, RED)),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ],
    )
    header = Table(
        [
            [
                [_p("AI Safety Lab", styles["eyebrow"]), Spacer(1, 8), _p("Evaluation Report", styles["title"])],
                badge,
            ]
        ],
        colWidths=[120 * mm, 62 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header)
    story.append(Spacer(1, 10))
    story.append(
        _table(
            [[""]],
            [182 * mm],
            [("LINEABOVE", (0, 0), (-1, -1), 2, RED)],
        )
    )
    story.append(Spacer(1, 10))


def _metadata_grid(story: list[object], styles: dict[str, ParagraphStyle], system_case: SystemCase) -> None:
    cells = [
        ("SYSTEM", system_case.title),
        ("SOURCE", _source_type_label(system_case)),
        ("TARGETS", _targets_label(system_case)),
        ("DATE", system_case.created_at.date().isoformat()),
    ]
    data = [
        [_p(label, styles["small_label"]) for label, _ in cells],
        [_p(value, styles["body"]) for _, value in cells],
    ]
    story.append(
        _table(
            data,
            [36 * mm, 54 * mm, 50 * mm, 42 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, -1), BG_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                ("TOPPADDING", (0, 1), (-1, 1), 8),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 14),
            ],
        )
    )


def _final_assessment_block(
    story: list[object], styles: dict[str, ParagraphStyle], final_view: dict[str, object]
) -> None:
    story.append(Spacer(1, 22))
    story.append(_p("Final assessment", styles["section"]))
    metrics = [
        ("VERDICT", _p(str(final_view["verdict"]), styles["metric_compact_red"]), BG_LIGHT_RED),
        ("RISK LEVEL", _p(str(final_view["risk_level"]), styles["metric_compact_gold"]), BG_LIGHT_RED),
        ("CONFIDENCE", _p(str(final_view["confidence"]), styles["metric_compact_blue"]), BG_LIGHT_RED),
        ("RISK SCORE", _p(f'{final_view["risk_score"]} / 5', styles["metric_compact"]), BG_LIGHT_RED),
    ]
    story.append(
        _table(
            [
                [_p(label, styles["small_label"]) for label, _, _ in metrics],
                [value for _, value, _ in metrics],
            ],
            [45.5 * mm, 45.5 * mm, 45.5 * mm, 45.5 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, 0), BG_LIGHT_RED),
                ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor("#F6B4B4")),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, 1), 16),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 16),
            ],
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        _table(
            [[_p("Recommendation", styles["small_label"]), _p(str(final_view["recommendation"]), styles["recommendation_metric"])]],
            [45.5 * mm, 136.5 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT_RED),
                ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor("#F6B4B4")),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ],
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        _table(
            [[
                _p("Color guide", styles["small_label"]),
                _p(f"<font color='{_html_color(RED)}'>■</font> Unsafe / High risk", styles["body_muted"]),
                _p(f"<font color='{_html_color(GOLD)}'>■</font> Needs review / Medium", styles["body_muted"]),
                _p(f"<font color='{_html_color(TEAL)}'>■</font> Safe / Low risk", styles["body_muted"]),
                _p(f"<font color='{_html_color(BLUE)}'>■</font> Informational", styles["body_muted"]),
            ]],
            [22 * mm, 40 * mm, 44 * mm, 34 * mm, 42 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, -1), BG_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
                ("LINEAFTER", (0, 0), (0, 0), 0.5, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ],
        )
    )


def _top_risks_block(story: list[object], styles: dict[str, ParagraphStyle], judge_outputs: list[JudgeOutput]) -> None:
    story.append(Spacer(1, 22))
    story.append(_p("Top risks", styles["section"]))
    for label, rationale in _top_risks(judge_outputs):
        row_color = RISK_ROW_COLORS.get(label, RED)
        story.append(
            _table(
                [
                    [
                        "",
                        _p(
                            f"<b>{label}</b>",
                            ParagraphStyle(
                                "risk_label",
                                parent=styles["body_small"],
                                fontName="Helvetica-Bold",
                                fontSize=8,
                                leading=11,
                                textColor=row_color,
                            ),
                        ),
                        _p(rationale, styles["body"]),
                    ]
                ],
                [1.2 * mm, 31 * mm, 149.8 * mm],
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
                    ("BACKGROUND", (0, 0), (0, 0), row_color),
                    ("BACKGROUND", (1, 0), (1, 0), BG_SOFT),
                    ("LINEAFTER", (1, 0), (1, 0), 0.5, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (1, 0), (1, 0), 10),
                    ("RIGHTPADDING", (1, 0), (1, 0), 8),
                    ("LEFTPADDING", (2, 0), (2, 0), 10),
                    ("RIGHTPADDING", (2, 0), (2, 0), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("ROUNDEDCORNERS", [4]),
                ],
            )
        )
        story.append(Spacer(1, 7))


def _framework_alignment_block(
    story: list[object], styles: dict[str, ParagraphStyle], final_view: dict[str, object]
) -> None:
    story.append(Spacer(1, 18))
    story.append(_p("Framework alignment", styles["section"]))
    story.append(
        _p(
            "The UNICC Review Framework is aligned to principles from NIST AI RMF and supports assessment against selected governance, transparency, traceability, robustness, and oversight themes reflected in ISO/IEC 42001 and the EU AI Act.",
            styles["body_muted"],
        )
    )
    story.append(Spacer(1, 8))
    for item in final_view.get("framework_alignment", []):
        story.append(
            _table(
                [
                    [_p(f"<b>{item['label']}</b>", styles["body"])],
                    [
                        _p("NIST AI RMF", styles["small_label"]),
                        _p("ISO/IEC 42001", styles["small_label"]),
                        _p("EU AI Act", styles["small_label"]),
                    ],
                    [
                        _p(", ".join(item["nist"]), styles["body_small"]),
                        _p(", ".join(item["iso"]), styles["body_small"]),
                        _p(", ".join(item["eu"]), styles["body_small"]),
                    ],
                ],
                [182 * mm],
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
                    ("BACKGROUND", (0, 0), (-1, 0), BG_SOFT),
                    ("INNERGRID", (0, 1), (-1, -1), 0.5, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ],
            )
        )
        grid = _table(
            [
                [
                    _p(", ".join(item["nist"]), styles["body_small"]),
                    _p(", ".join(item["iso"]), styles["body_small"]),
                    _p(", ".join(item["eu"]), styles["body_small"]),
                ]
            ],
            [60.6 * mm, 60.6 * mm, 60.8 * mm],
            [
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ],
        )
        story[-1] = _table(
            [
                [_p(f"<b>{item['label']}</b>", styles["body"])],
                [
                    _p("NIST AI RMF", styles["small_label"]),
                    _p("ISO/IEC 42001", styles["small_label"]),
                    _p("EU AI Act", styles["small_label"]),
                ],
                [
                    _p(", ".join(item["nist"]), styles["body_small"]),
                    _p(", ".join(item["iso"]), styles["body_small"]),
                    _p(", ".join(item["eu"]), styles["body_small"]),
                ],
            ],
            [60.6 * mm, 60.6 * mm, 60.8 * mm],
            [
                ("SPAN", (0, 0), (-1, 0)),
                ("BACKGROUND", (0, 0), (-1, 0), BG_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
                ("INNERGRID", (0, 1), (-1, -1), 0.5, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ],
        )
        story.append(Spacer(1, 6))


def _control_assessment_block(
    story: list[object], styles: dict[str, ParagraphStyle], final_view: dict[str, object]
) -> None:
    story.append(Spacer(1, 18))
    story.append(_p("Control assessment", styles["section"]))
    story.append(
        _p(
            "These controls are assessment-oriented signals derived from the current evidence bundle. They support structured assurance review and remediation planning, but do not constitute a certification or legal compliance determination.",
            styles["body_muted"],
        )
    )
    story.append(Spacer(1, 8))
    for control in final_view.get("control_assessment", []):
        evidence_text = "<br/>".join(f"• {item}" for item in control["evidence"])
        status_color = CONTROL_STATUS_COLORS.get(str(control["status"]), GOLD)
        status_bg = CONTROL_STATUS_BACKGROUNDS.get(str(control["status"]), BG_LIGHT_GOLD)
        header = _table(
            [[
                _p(
                    f"<b>{control['label']}</b>",
                    ParagraphStyle(
                        "control_title",
                        parent=styles["body"],
                        fontName="Helvetica-Bold",
                        fontSize=10,
                        leading=14,
                        textColor=TEXT_DARK,
                    ),
                ),
                _p(
                    f"<font color='{_html_color(status_color)}'><b>{control['status']}</b></font>",
                    ParagraphStyle(
                        "control_status",
                        parent=styles["body_small"],
                        fontName="Helvetica-Bold",
                        fontSize=8,
                        leading=11,
                        textColor=status_color,
                    ),
                ),
                _p(f"Score: {control['average_score']} / 5", styles["body_muted"]),
                _p(f"Mapped: {', '.join(control['categories'])}", styles["body_muted"]),
            ]],
            [60 * mm, 34 * mm, 26 * mm, 62 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, -1), status_bg),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ],
        )
        description = _table(
            [[_p(control["description"], styles["body_small"])]],
            [182 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ],
        )
        summary = _table(
            [[_p(control["status_summary"], styles["body_muted"])]],
            [182 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, -1), BG_SOFT),
                ("LINEABOVE", (0, 0), (-1, 0), 0.5, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ],
        )
        evidence = _table(
            [
                [_p("Supporting evidence", styles["small_label"])],
                [_p(evidence_text or "No supporting evidence was surfaced for this control.", styles["body_small"])],
            ],
            [182 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("LINEABOVE", (0, 0), (-1, 0), 0.5, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 7),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
            ],
        )
        card = _table(
            [[header], [description], [summary], [evidence]],
            [182 * mm],
            [
                ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
                ("LINEBEFORE", (0, 0), (0, -1), 3, status_color),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("ROUNDEDCORNERS", [6]),
            ],
        )
        story.append(KeepTogether([card, Spacer(1, 6)]))


def _alignment_block(
    story: list[object],
    styles: dict[str, ParagraphStyle],
    reviewer_views: list[dict[str, object]],
    final_view: dict[str, object],
) -> None:
    story.append(_p("Reviewer alignment", styles["section"]))
    rows = [[
        _p("REVIEWER", styles["small_label"]),
        _p("VERDICT", styles["small_label"]),
        _p("RISK SCORE", styles["small_label"]),
        _p("CONFIDENCE", styles["small_label"]),
    ]]
    for view in reviewer_views:
        verdict_text = str(view["verdict"])
        rows.append(
            [
                _p(str(view["label"]), styles["body"]),
                _p(f"<font color='{_html_color(VERDICT_COLORS.get(verdict_text, RED))}'><b>{verdict_text}</b></font>", styles["body"]),
                _p(str(view["risk_score"]), styles["body"]),
                _p(str(view["confidence"]), styles["body"]),
            ]
        )
    story.append(
        _table(
            rows,
            [56 * mm, 42 * mm, 35 * mm, 49 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, 0), BG_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ],
        )
    )
    story.append(Spacer(1, 8))
    alignment = final_view["alignment"]
    story.append(
        _table(
            [[
                _p("Alignment status", styles["small_label"]),
                _p(f"{alignment['label']} — {alignment['summary']}", styles["body"]),
            ]],
            [38 * mm, 144 * mm],
            [
                ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT_GOLD),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#F1D28B")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ],
        )
    )


def _reviewer_card(
    story: list[object],
    styles: dict[str, ParagraphStyle],
    view: dict[str, object],
) -> None:
    verdict = str(view["verdict"])
    header_bg = BG_LIGHT_GOLD if verdict == "Needs Review" else BG_LIGHT_RED if verdict == "Unsafe" else colors.HexColor("#EAF7EF")
    verdict_color = VERDICT_COLORS.get(verdict, TEXT_DARK)
    key_risks = list(view.get("key_risks") or view.get("main_reasons") or view.get("reasons") or [])
    mitigations = list(view.get("mitigations") or view.get("required_actions") or [])
    category_highlights = list(view.get("category_highlights") or [])
    if not category_highlights and view.get("risk_level"):
        category_highlights = [f"Final risk level: {view['risk_level']}"]
    summary = str(view.get("summary") or "")
    header_table = _table(
        [[
            _p(f"<b>{view['label']}</b>", styles["reviewer_name"]),
            _p(f"<font color='{_html_color(verdict_color)}'><b>{verdict}</b></font>", styles["body"]),
            _p(f"Confidence: {view['confidence']}", styles["body_muted"]),
        ]],
        [68 * mm, 45 * mm, 69 * mm],
        [
            ("BACKGROUND", (0, 0), (-1, -1), header_bg),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ],
    )
    meta_table = _table(
        [
            [_p("RISK SCORE", styles["small_label"]), _p("RISK LEVEL", styles["small_label"]), _p("CATEGORIES", styles["small_label"])],
            [
                _p(str(view["risk_score"]), styles["metric_red"] if verdict == "Unsafe" else styles["metric_gold"]),
                _p(str(view["risk_level"]), _risk_level_style(str(view["risk_level"]), styles)),
                _p(" · ".join(str(item) for item in category_highlights), styles["body_muted"]),
            ],
        ],
        [32 * mm, 42 * mm, 108 * mm],
        [
            ("INNERGRID", (0, 0), (-1, -1), 0.75, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
            ("TOPPADDING", (0, 1), (-1, 1), 5),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
        ],
    )
    key_risks_text = "<br/>".join(f"• {item}" for item in key_risks)
    mitigations_text = "<br/>".join(f"• {item}" for item in mitigations)
    two_col_table = _table(
        [
            [_p("Key risks", styles["subhead"]), _p("Recommendations", styles["subhead"])],
            [_p(key_risks_text or "No key risks recorded.", styles["body_small"]), _p(mitigations_text or "No recommendations recorded.", styles["body_small"])],
        ],
        [91 * mm, 91 * mm],
        [
            ("INNERGRID", (0, 0), (-1, -1), 0.75, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 1), (-1, 1), 8),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 12),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ],
    )
    summary_table = _table(
        [[_p("Summary", styles["small_label"]), _p(summary, styles["body_muted"])]],
        [22 * mm, 160 * mm],
        [
            ("BACKGROUND", (0, 0), (-1, -1), BG_SOFT),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ],
    )
    card = _table(
        [[header_table], [meta_table], [two_col_table], [summary_table]],
        [182 * mm],
        [
            ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
            ("LINEBEFORE", (0, 0), (0, -1), 3, verdict_color),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ROUNDEDCORNERS", [6]),
        ],
    )
    story.append(KeepTogether([card, Spacer(1, 10)]))


def _required_actions_page(
    story: list[object],
    styles: dict[str, ParagraphStyle],
    final_view: dict[str, object],
    settings: AppConfig,
) -> None:
    story.append(PageBreak())
    story.append(_p("Required actions", styles["section"]))
    for index, action in enumerate(final_view["required_actions"], start=1):
        story.append(
            _table(
                [[
                    _p(
                        str(index),
                        ParagraphStyle(
                            "action_num",
                            parent=styles["body"],
                            fontName="Helvetica-Bold",
                            fontSize=14,
                            leading=18,
                            textColor=colors.white,
                            alignment=TA_LEFT,
                        ),
                    ),
                    _p(
                        f"<b>{_action_label(action, index)}</b>",
                        ParagraphStyle(
                            "action_label",
                            parent=styles["body_small"],
                            fontName="Helvetica-Bold",
                            fontSize=8,
                            leading=11,
                            textColor=RED,
                        ),
                    ),
                    _p(action, styles["body"]),
                ]],
                [10 * mm, 32 * mm, 140 * mm],
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, BORDER),
                    ("BACKGROUND", (0, 0), (0, 0), RED),
                    ("BACKGROUND", (1, 0), (1, 0), BG_LIGHT_RED),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ],
            )
        )
        story.append(Spacer(1, 7))
    story.append(Spacer(1, 20))
    story.append(
        _table(
            [[_p("Run metadata", styles["small_label"]), _p(_metadata_footer(settings), styles["mono"])]],
            [28 * mm, 154 * mm],
            [
                ("LINEABOVE", (0, 0), (-1, -1), 0.75, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ],
        )
    )


def generate_report_pdf(
    *,
    output_path: Path,
    system_case: SystemCase,
    judge_outputs: list[JudgeOutput],
    final_output: FinalJudgeOutput,
    settings: AppConfig,
) -> None:
    styles = _styles()
    reviewer_views = _reviewer_rows(judge_outputs)
    final_view = final_assessment_view(final_output, judge_outputs)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=18 * mm,
    )
    story: list[object] = []

    _cover_header(story, styles, final_view)
    _metadata_grid(story, styles, system_case)
    _final_assessment_block(story, styles, final_view)
    _top_risks_block(story, styles, judge_outputs)
    _framework_alignment_block(story, styles, final_view)
    _control_assessment_block(story, styles, final_view)

    story.append(PageBreak())
    _alignment_block(story, styles, reviewer_views, final_view)
    story.append(Spacer(1, 22))
    story.append(_p("Expert reviewer breakdown", styles["section"]))
    for reviewer in reviewer_views:
        _reviewer_card(story, styles, reviewer)

    story.append(PageBreak())
    _reviewer_card(story, styles, final_view)
    _required_actions_page(story, styles, final_view, settings)

    doc.build(story, onFirstPage=_page_chrome, onLaterPages=_page_chrome)
