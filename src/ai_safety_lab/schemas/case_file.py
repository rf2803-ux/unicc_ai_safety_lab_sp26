from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ToolLog(BaseModel):
    phase: str | None = None
    tool_name: str
    input: str | dict[str, Any]
    output: str | dict[str, Any]
    timestamp: datetime | None = None


class MemoryLog(BaseModel):
    event_type: str
    content: str | dict[str, Any]
    timestamp: datetime | None = None
    blocked: bool | None = None


class CaseFile(BaseModel):
    case_id: str
    created_at: datetime
    target_model: str
    transcript: list[Message] = Field(min_length=1)
    tool_logs: list[ToolLog]
    memory_logs: list[MemoryLog]
