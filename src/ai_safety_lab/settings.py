from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv()


class ProviderConfig(BaseModel):
    backend: str
    model: str


class AppConfig(BaseModel):
    app_name: str = "AI Safety Lab"
    default_output_dir: str = "runs"
    allow_ultimate_judge_raw_transcript: bool = False
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_app_config(config_path: str | Path | None = None) -> AppConfig:
    data: dict[str, Any] = {}

    base_path = Path("config/config.example.yaml")
    if base_path.exists():
        data = yaml.safe_load(base_path.read_text()) or {}

    override_path: Path | None = None
    if config_path is not None:
        override_path = Path(config_path)
    elif os.getenv("APP_CONFIG_PATH"):
        override_path = Path(os.getenv("APP_CONFIG_PATH", ""))
    else:
        override_path = Path("config/config.local.yaml")

    if override_path.exists():
        override_data = yaml.safe_load(override_path.read_text()) or {}
        data = _deep_merge(data, override_data)

    return AppConfig.model_validate(data)
