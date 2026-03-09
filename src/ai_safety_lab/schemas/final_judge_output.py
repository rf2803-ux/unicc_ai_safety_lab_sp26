from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, conint, model_validator

from .judge_output import Confidence, Verdict


class AgreementItem(BaseModel):
    judge_id: Literal["judge1", "judge2", "judge3"]
    verdict: Verdict
    main_reasons: list[str]


class FinalJudgeOutput(BaseModel):
    judge_id: Literal["ultimate_judge"] = "ultimate_judge"
    backend: str
    model: str
    based_on_judges: list[str] = Field(min_length=3, max_length=3)
    final_verdict: Verdict
    final_score: conint(ge=0, le=5)
    agreement_summary: list[AgreementItem] = Field(min_length=3, max_length=3)
    key_conflicts: list[str]
    final_rationale: str
    required_actions: list[str]
    confidence: Confidence
    governance_mapping: list[str]

    @model_validator(mode="after")
    def validate_judge_ids(self) -> "FinalJudgeOutput":
        expected = {"judge1", "judge2", "judge3"}
        if set(self.based_on_judges) != expected:
            raise ValueError("based_on_judges must include judge1, judge2, and judge3")
        if {item.judge_id for item in self.agreement_summary} != expected:
            raise ValueError("agreement_summary must include judge1, judge2, and judge3")
        return self
