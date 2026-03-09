from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_safety_lab.schemas import CaseFile


def test_case_file_schema_accepts_valid_payload() -> None:
    payload = {
        "case_id": "demo_001",
        "created_at": "2026-03-09T12:00:00Z",
        "target_model": "dummy-target",
        "transcript": [{"role": "user", "content": "Hello"}],
        "tool_logs": [],
        "memory_logs": [],
    }
    case_file = CaseFile.model_validate(payload)
    assert case_file.case_id == "demo_001"


def test_case_file_requires_forward_compatible_fields() -> None:
    payload = {
        "case_id": "demo_001",
        "created_at": "2026-03-09T12:00:00Z",
        "target_model": "dummy-target",
        "transcript": [{"role": "user", "content": "Hello"}],
    }
    with pytest.raises(ValidationError):
        CaseFile.model_validate(payload)
