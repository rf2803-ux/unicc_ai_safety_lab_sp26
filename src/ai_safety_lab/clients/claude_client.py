from __future__ import annotations

import os

from .base import BaseLLMClient, MissingAPIKeyError


_CLAUDE_TIMEOUT_SECONDS = float(os.getenv("ANTHROPIC_TIMEOUT_SECONDS", "600"))
_CLAUDE_MAX_RETRIES = int(os.getenv("ANTHROPIC_MAX_RETRIES", "2"))


class ClaudeClient(BaseLLMClient):
    def __init__(self, model: str, api_key: str | None = None):
        super().__init__(model=model, api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        if not self.api_key:
            raise MissingAPIKeyError(
                "ANTHROPIC_API_KEY is missing. Set it as an environment variable or in your local .env file."
            )
        from anthropic import Anthropic

        self.client = Anthropic(
            api_key=self.api_key,
            timeout=_CLAUDE_TIMEOUT_SECONDS,
            max_retries=_CLAUDE_MAX_RETRIES,
        )

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(block.text for block in response.content if getattr(block, "text", None))
