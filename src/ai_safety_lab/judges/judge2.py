from __future__ import annotations

from ai_safety_lab.judges.base import BaseJudge


class Judge2(BaseJudge):
    judge_id = "judge2"
    lens = "adversarial security reviewer"

    def __init__(self, backend: str, model: str):
        super().__init__(backend=backend, model=model, prompt_path="config/prompts/judge2_system.md")
