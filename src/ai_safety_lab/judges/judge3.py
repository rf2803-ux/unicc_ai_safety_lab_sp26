from __future__ import annotations

from ai_safety_lab.judges.base import BaseJudge


class Judge3(BaseJudge):
    judge_id = "judge3"
    lens = "user impact and fairness reviewer"

    def __init__(self, backend: str, model: str):
        super().__init__(backend=backend, model=model, prompt_path="config/prompts/judge3_system.md")
