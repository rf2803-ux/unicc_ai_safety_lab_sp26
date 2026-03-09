from __future__ import annotations

from ai_safety_lab.judges.base import BaseJudge


class Judge1(BaseJudge):
    judge_id = "judge1"
    lens = "conservative compliance reviewer"

    def __init__(self, backend: str, model: str):
        super().__init__(backend=backend, model=model, prompt_path="config/prompts/judge1_system.md")
