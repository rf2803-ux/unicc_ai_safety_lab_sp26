from __future__ import annotations

import os

from .base import BaseLLMClient, MissingAPIKeyError, ProviderResponseError


_GEMINI_TIMEOUT_SECONDS = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "600"))
_GEMINI_TIMEOUT_MILLISECONDS = int(_GEMINI_TIMEOUT_SECONDS * 1000)
_GEMINI_RETRY_ATTEMPTS = int(os.getenv("GEMINI_MAX_RETRIES", "2"))


class GeminiClient(BaseLLMClient):
    def __init__(self, model: str, api_key: str | None = None):
        super().__init__(model=model, api_key=api_key or os.getenv("GEMINI_API_KEY"))
        if not self.api_key:
            raise MissingAPIKeyError(
                "GEMINI_API_KEY is missing. Set it as an environment variable or in your local .env file."
            )
        from google import genai
        from google.genai import errors, types

        self._errors = errors
        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(
                timeout=_GEMINI_TIMEOUT_MILLISECONDS,
                retry_options=types.HttpRetryOptions(
                    attempts=_GEMINI_RETRY_ATTEMPTS,
                    initial_delay=1.0,
                    max_delay=4.0,
                    exp_base=2.0,
                    jitter=0.25,
                    http_status_codes=[429, 500, 502, 503, 504],
                ),
            ),
        )

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        from google.genai import types

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                ),
            )
        except self._errors.APIError as exc:
            raise ProviderResponseError(f"Gemini request failed: {exc}") from exc
        except Exception as exc:
            raise ProviderResponseError(f"Gemini request failed: {exc}") from exc

        text = (response.text or "").strip()
        if not text:
            raise ProviderResponseError("Gemini returned an empty response.")
        return text
