from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_safety_lab.schemas import FinalJudgeOutput
from tests.helpers import sample_final_output


def test_final_judge_output_accepts_valid_payload() -> None:
    output = sample_final_output()
    assert output.final_verdict == "SAFE"


def test_final_judge_output_requires_all_three_judges() -> None:
    payload = sample_final_output().model_dump(mode="json")
    payload["agreement_summary"] = payload["agreement_summary"][:2]
    with pytest.raises(ValidationError):
        FinalJudgeOutput.model_validate(payload)
