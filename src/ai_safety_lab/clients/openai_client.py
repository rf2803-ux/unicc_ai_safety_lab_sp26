from __future__ import annotations

import os

from .base import BaseLLMClient, MissingAPIKeyError


_OPENAI_TIMEOUT_SECONDS = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "600"))
_OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "2"))


class OpenAIClient(BaseLLMClient):
    def __init__(self, model: str, api_key: str | None = None):
        super().__init__(model=model, api_key=api_key or os.getenv("OPENAI_API_KEY"))
        if not self.api_key:
            raise MissingAPIKeyError(
                "OPENAI_API_KEY is missing. Set it as an environment variable or in your local .env file."
            )
        from openai import OpenAI

        self.client = OpenAI(
            api_key=self.api_key,
            timeout=_OPENAI_TIMEOUT_SECONDS,
            max_retries=_OPENAI_MAX_RETRIES,
        )

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.output_text
