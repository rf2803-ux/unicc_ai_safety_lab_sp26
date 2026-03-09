from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ValidationError


class MissingAPIKeyError(RuntimeError):
    """Raised when a provider key is missing."""


class ProviderResponseError(RuntimeError):
    """Raised when a provider returns invalid JSON."""


class BaseLLMClient(ABC):
    def __init__(self, model: str, api_key: str | None = None):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> BaseModel:
        raw_text = self.generate_text(system_prompt=system_prompt, user_prompt=user_prompt)
        try:
            payload: Any = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ProviderResponseError(f"Model did not return valid JSON: {exc}") from exc
        try:
            return response_schema.model_validate(payload)
        except ValidationError as exc:
            raise ProviderResponseError(f"Model JSON did not match schema: {exc}") from exc
