from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError


load_dotenv()


class MissingAPIKeyError(RuntimeError):
    """Raised when a provider key is missing."""


class ProviderResponseError(RuntimeError):
    """Raised when a provider returns invalid JSON."""


def extract_json_payload(raw_text: str) -> Any:
    text = raw_text.strip()
    if not text:
        raise ProviderResponseError("Model returned an empty response instead of JSON.")

    candidates = [text]

    fenced_matches = re.findall(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    candidates.extend(match.strip() for match in fenced_matches if match.strip())

    json_start = min((idx for idx in (text.find("{"), text.find("[")) if idx != -1), default=-1)
    if json_start != -1:
        candidates.append(text[json_start:].strip())

    decoder = json.JSONDecoder()
    for candidate in candidates:
        try:
            payload, _ = decoder.raw_decode(candidate)
            return payload
        except json.JSONDecodeError:
            continue

    preview = text[:300].replace("\n", "\\n")
    raise ProviderResponseError(f"Model did not return valid JSON. Response preview: {preview}")


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
        payload: Any = extract_json_payload(raw_text)
        try:
            return response_schema.model_validate(payload)
        except ValidationError as exc:
            preview = raw_text.strip()[:300].replace("\n", "\\n")
            raise ProviderResponseError(
                f"Model JSON did not match schema: {exc}. Response preview: {preview}"
            ) from exc
