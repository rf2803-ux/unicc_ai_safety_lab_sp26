from __future__ import annotations

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


def load_app_config(config_path: str | Path | None = None) -> AppConfig:
    path = Path(config_path or "config/config.example.yaml")
    data: dict[str, Any] = {}
    if path.exists():
        data = yaml.safe_load(path.read_text()) or {}
    return AppConfig.model_validate(data)
