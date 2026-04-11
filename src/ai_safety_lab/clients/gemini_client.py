from __future__ import annotations

import os

from .base import BaseLLMClient, MissingAPIKeyError


class GeminiClient(BaseLLMClient):
    def __init__(self, model: str, api_key: str | None = None):
        super().__init__(model=model, api_key=api_key or os.getenv("GEMINI_API_KEY"))
        if not self.api_key:
            raise MissingAPIKeyError(
                "GEMINI_API_KEY is missing. Set it as an environment variable or in your local .env file."
            )
        import google.generativeai as genai

        self._genai = genai
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.generate_content([system_prompt, user_prompt])
        return response.text
