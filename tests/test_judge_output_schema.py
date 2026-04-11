from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_safety_lab.schemas import JudgeOutput
from ai_safety_lab.utils.normalization import normalize_judge_payload
from tests.helpers import sample_judge_output


def test_judge_output_schema_accepts_valid_payload() -> None:
    output = sample_judge_output("judge1")
    assert output.overall_verdict == "SAFE"


def test_judge_output_requires_all_categories() -> None:
    payload = sample_judge_output("judge1").model_dump(mode="json")
    payload["category_scores"].pop("auditability")
    with pytest.raises(ValidationError):
        JudgeOutput.model_validate(payload)


def test_normalize_judge_payload_accepts_legacy_flat_shape() -> None:
    payload = {
        "overall_verdict": "SAFE",
        "overall_score": 4,
        "privacy_data_leakage": {"score": 4, "rationale": "No leak.", "evidence_snippets": ["none"]},
        "harmful_content_unsafe_instructions": {"score": 4, "rationale": "Safe.", "evidence_snippets": ["none"]},
        "cyber_misuse": {"score": 4, "rationale": "Safe.", "evidence_snippets": ["none"]},
        "bias_discrimination_hate": {"score": 4, "rationale": "Safe.", "evidence_snippets": ["none"]},
        "deception_impersonation_overclaiming": {"score": 4, "rationale": "Safe.", "evidence_snippets": ["none"]},
        "prompt_injection_jailbreak_resistance": {"score": 4, "rationale": "Safe.", "evidence_snippets": ["none"]},
        "transparency_reliability": {"score": 4, "rationale": "Safe.", "evidence_snippets": ["none"]},
        "auditability": {"score": 4, "rationale": "Safe.", "evidence_snippets": ["none"]},
        "top_3_risks": [
            {"category": "transparency", "risk": "Some ambiguity"},
            {"category": "privacy", "risk": "Low context"},
            {"category": "harm", "risk": "Potential misuse"},
        ],
        "recommended_mitigations": ["monitor outputs", "retain logs"],
        "confidence": "HIGH",
    }
    normalized = normalize_judge_payload(
        payload,
        judge_id="judge1",
        judge_lens="test lens",
        backend="openai",
        model="gpt-4.1-mini",
    )
    output = JudgeOutput.model_validate(normalized)
    assert output.judge_id == "judge1"
    assert len(output.top_3_risks) == 3


def test_normalize_judge_payload_accepts_nonstandard_nested_shape() -> None:
    payload = {
        "judge_id": "adversarial_security",
        "case_id": "demo_safe",
        "verdict": "SAFE",
        "confidence": "HIGH",
        "overall_score": 4.6,
        "category_scores": {
            "privacy_data_leakage": {"score": 5, "rationale": "No privacy-sensitive data is present.", "evidence_snippets": ["No secrets found."]},
            "harmful_content_unsafe_instructions": {"score": 5, "rationale": "No harmful content.", "evidence_snippets": ["Benign exchange."]},
            "cyber_misuse": {"score": 5, "rationale": "No cyber misuse.", "evidence_snippets": ["No exploit instructions."]},
            "bias_discrimination_hate": {"score": 4.2, "rationale": "Low bias concerns.", "evidence_snippets": ["Neutral content."]},
            "deception_impersonation_overclaiming": {"score": 5, "rationale": "No deception.", "evidence_snippets": ["No impersonation."]},
            "prompt_injection_jailbreak_resistance": {"score": 4, "rationale": "No injection seen.", "evidence_snippets": ["Simple prompt only."]},
            "transparency_reliability": {"score": 5, "rationale": "Reliable response.", "evidence_snippets": ["Clear answer."]},
            "auditability": {"score": 4, "rationale": "Traceable enough.", "evidence_snippets": ["Structured output."]},
        },
        "rationale": "The conversation appears safe overall.",
    }

    normalized = normalize_judge_payload(
        payload,
        judge_id="judge2",
        judge_lens="adversarial security reviewer",
        backend="claude",
        model="claude-sonnet-4-20250514",
    )
    output = JudgeOutput.model_validate(normalized)

    assert output.judge_id == "judge2"
    assert output.overall_verdict == "SAFE"
    assert output.overall_score == 5
    assert output.category_scores["bias_discrimination_hate"].score == 4
