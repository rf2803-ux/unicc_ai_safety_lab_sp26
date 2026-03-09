from __future__ import annotations

import os

from .base import BaseLLMClient, MissingAPIKeyError


class OpenAIClient(BaseLLMClient):
    def __init__(self, model: str, api_key: str | None = None):
        super().__init__(model=model, api_key=api_key or os.getenv("OPENAI_API_KEY"))
        if not self.api_key:
            raise MissingAPIKeyError("OPENAI_API_KEY is missing. Set it in your local .env file.")
        from openai import OpenAI

        self.client = OpenAI(api_key=self.api_key)

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.output_text
