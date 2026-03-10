from __future__ import annotations

from abc import ABC
from pathlib import Path

from pydantic import ValidationError

from ai_safety_lab.clients import ClaudeClient, GeminiClient, LlamaClient, OpenAIClient
from ai_safety_lab.clients.base import ProviderResponseError, extract_json_payload
from ai_safety_lab.constants import CATEGORY_KEYS
from ai_safety_lab.schemas import CaseFile, JudgeOutput
from ai_safety_lab.utils.json_io import read_text
from ai_safety_lab.utils.normalization import normalize_judge_payload, recover_judge_payload_from_text


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


class BaseJudge(ABC):
    judge_id: str
    lens: str

    def __init__(self, backend: str, model: str, prompt_path: str):
        self.backend = backend
        self.model = model
        self.prompt_path = prompt_path
        self.client = build_client(backend=backend, model=model)

    def _system_prompt(self) -> str:
        shared = read_text(Path("config/prompts/shared_rubric.md"))
        lens = read_text(Path(self.prompt_path))
        return f"{shared}\n\n{lens}"

    def _user_prompt(self, case_file: CaseFile) -> str:
        return (
            "Evaluate this case file holistically using the rubric. "
            "Return strict JSON only.\n\n"
            f"{case_file.model_dump_json(indent=2)}"
        )

    def evaluate(self, case_file: CaseFile) -> JudgeOutput:
        raw_text = self.client.generate_text(
            system_prompt=self._system_prompt(),
            user_prompt=self._user_prompt(case_file),
        )
        try:
            payload = extract_json_payload(raw_text)
            if not isinstance(payload, dict):
                preview = str(payload)[:300].replace("\n", "\\n")
                raise ProviderResponseError(f"Judge response must be a JSON object. Response preview: {preview}")
        except ProviderResponseError:
            payload = recover_judge_payload_from_text(raw_text)
        normalized_payload = normalize_judge_payload(
            payload,
            judge_id=self.judge_id,
            judge_lens=self.lens,
            backend=self.backend,
            model=self.model,
        )
        try:
            output = JudgeOutput.model_validate(normalized_payload)
        except ValidationError as exc:
            preview = raw_text.strip()[:300].replace("\n", "\\n")
            raise ProviderResponseError(
                f"Model JSON did not match schema: {exc}. Response preview: {preview}"
            ) from exc
        if set(output.category_scores.keys()) != set(CATEGORY_KEYS):
            raise ValueError("Judge output must include all eight required rubric categories.")
        return output
