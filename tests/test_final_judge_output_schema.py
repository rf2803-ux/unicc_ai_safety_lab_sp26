from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_safety_lab.schemas import FinalJudgeOutput
from ai_safety_lab.utils.normalization import normalize_final_judge_payload
from tests.helpers import sample_final_output


def test_final_judge_output_accepts_valid_payload() -> None:
    output = sample_final_output()
    assert output.final_verdict == "SAFE"


def test_final_judge_output_requires_all_three_judges() -> None:
    payload = sample_final_output().model_dump(mode="json")
    payload["agreement_summary"] = payload["agreement_summary"][:2]
    with pytest.raises(ValidationError):
        FinalJudgeOutput.model_validate(payload)


def test_normalize_final_judge_payload_accepts_mapping_variants() -> None:
    payload = {
        "final_verdict": "NEEDS_REVIEW",
        "final_score": 3,
        "agreement_summary": {
            "privacy_data_leakage": "All judges identified meaningful privacy exposure.",
            "cyber_misuse": "Security concerns were elevated because of the upload surface.",
        },
        "key_conflicts": {
            "severity_and_final_verdict": "Judge 2 was stricter than the others on technical specifics."
        },
        "final_rationale": "The panel agreed on meaningful risks with some disagreement on severity.",
        "required_actions": ["Add stronger access controls"],
        "confidence": "MED",
        "governance_mapping": ["EU:Robustness"],
    }

    normalized = normalize_final_judge_payload(payload, backend="openai", model="gpt-4.1-mini")
    output = FinalJudgeOutput.model_validate(normalized)

    assert len(output.agreement_summary) == 3
    assert output.key_conflicts
