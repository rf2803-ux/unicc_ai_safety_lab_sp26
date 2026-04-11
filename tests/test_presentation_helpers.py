from __future__ import annotations

from ai_safety_lab.reporting.presentation import (
    clean_bullets,
    control_assessment_view,
    final_assessment_view,
    framework_alignment_for_category,
    reviewer_alignment_summary,
    reviewer_panel_view,
)
from tests.helpers import sample_final_output, sample_judge_output


def test_clean_bullets_removes_raw_formatting_noise() -> None:
    values = ['[ "Privacy risk" ]', '0: "Auditability issue"', " Privacy risk "]

    cleaned = clean_bullets(values)

    assert cleaned == ["Privacy risk", "Auditability issue"]


def test_reviewer_panel_view_formats_reviewer_output() -> None:
    view = reviewer_panel_view(sample_judge_output("judge1"))

    assert view["label"] == "Expert Reviewer A"
    assert view["verdict"] == "Safe"
    assert view["confidence"] == "High"
    assert view["key_risks"]
    assert view["category_details"]


def test_final_assessment_view_summarizes_existing_data_only() -> None:
    judges = [
        sample_judge_output("judge1"),
        sample_judge_output("judge2"),
        sample_judge_output("judge3"),
    ]
    view = final_assessment_view(sample_final_output(), judges)

    assert view["label"] == "Final Assessment"
    assert view["recommendation"]
    assert view["reasons"]
    assert len(view["reasons"]) <= 5


def test_reviewer_alignment_summary_detects_strong_agreement() -> None:
    judges = [
        sample_judge_output("judge1"),
        sample_judge_output("judge2"),
        sample_judge_output("judge3"),
    ]

    summary = reviewer_alignment_summary(judges, sample_final_output())

    assert summary["label"] == "Strong Agreement"


def test_framework_alignment_for_category_returns_crosswalk() -> None:
    alignment = framework_alignment_for_category("auditability")

    assert alignment["label"] == "Auditability"
    assert alignment["nist"]
    assert alignment["iso"]
    assert alignment["eu"]


def test_control_assessment_view_returns_traceable_controls() -> None:
    judges = [
        sample_judge_output("judge1"),
        sample_judge_output("judge2"),
        sample_judge_output("judge3"),
    ]

    controls = control_assessment_view(judges)

    assert controls
    assert controls[0]["label"]
    assert controls[0]["status"] in {"Needs attention", "Review needed", "Better supported"}
    assert controls[0]["categories"]
    assert controls[0]["framework_alignment"]


def test_final_assessment_view_includes_control_assessment() -> None:
    judges = [
        sample_judge_output("judge1"),
        sample_judge_output("judge2"),
        sample_judge_output("judge3"),
    ]

    view = final_assessment_view(sample_final_output(), judges)

    assert view["control_assessment"]
