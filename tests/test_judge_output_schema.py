from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_safety_lab.schemas import JudgeOutput
from tests.helpers import sample_judge_output


def test_judge_output_schema_accepts_valid_payload() -> None:
    output = sample_judge_output("judge1")
    assert output.overall_verdict == "SAFE"


def test_judge_output_requires_all_categories() -> None:
    payload = sample_judge_output("judge1").model_dump(mode="json")
    payload["category_scores"].pop("auditability")
    with pytest.raises(ValidationError):
        JudgeOutput.model_validate(payload)
