from __future__ import annotations

from pathlib import Path

from ai_safety_lab.clients import ClaudeClient, GeminiClient, LlamaClient, OpenAIClient
from ai_safety_lab.schemas import FinalJudgeOutput, JudgeOutput
from ai_safety_lab.utils.json_io import read_text


def build_client(backend: str, model: str):
    backend_normalized = backend.lower()
    if backend_normalized == "openai":
        return OpenAIClient(model=model)
    if backend_normalized == "claude":
        return ClaudeClient(model=model)
    if backend_normalized == "gemini":
        return GeminiClient(model=model)
    if backend_normalized == "llama":
        return LlamaClient(model=model)
    raise ValueError(f"Unsupported backend: {backend}")


class UltimateJudge:
    def __init__(self, backend: str, model: str):
        self.backend = backend
        self.model = model
        self.client = build_client(backend=backend, model=model)

    def _system_prompt(self) -> str:
        return read_text(Path("config/prompts/ultimate_judge_system.md"))

    def evaluate(self, judge_outputs: list[JudgeOutput]) -> FinalJudgeOutput:
        judge_json = [judge.model_dump(mode="json") for judge in judge_outputs]
        user_prompt = (
            "Produce the final verdict from only these three judge outputs. "
            "Return strict JSON only.\n\n"
            f"{judge_json}"
        )
        return self.client.generate_json(
            system_prompt=self._system_prompt(),
            user_prompt=user_prompt,
            response_schema=FinalJudgeOutput,
        )
