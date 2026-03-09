from __future__ import annotations

from .base import BaseLLMClient


class LlamaClient(BaseLLMClient):
    def __init__(self, model: str, api_key: str | None = None):
        super().__init__(model=model, api_key=api_key)

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError(
            "LlamaClient is a placeholder for future local deployment. "
            "Wire it to your local inference server when the Llama environment is ready."
        )
