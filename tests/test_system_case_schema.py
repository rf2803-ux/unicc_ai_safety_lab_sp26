from __future__ import annotations

from ai_safety_lab.schemas import SystemCase


def test_system_case_schema_accepts_repository_payload() -> None:
    payload = {
        "case_id": "repo_verimedia",
        "created_at": "2026-04-10T12:00:00Z",
        "target_type": "repository",
        "title": "VeriMedia",
        "source_url": "https://github.com/FlashCarrot/VeriMedia",
        "source_metadata": {
            "frameworks": ["Flask"],
            "languages": ["Python"],
        },
        "capability_profile": {
            "model_backends": ["gpt-4o", "whisper"],
            "media_inputs": ["text", "audio", "video"],
        },
        "security_posture": {
            "authentication_signals": [
                {
                    "label": "auth_not_found",
                    "status": "unclear",
                    "summary": "No explicit authentication layer was found in the reviewed files.",
                    "source_refs": [{"path": "README.md", "source_kind": "readme"}],
                }
            ]
        },
        "evidence": {
            "inspected_files": [{"path": "README.md", "file_type": "markdown"}],
            "evidence_items": [
                {
                    "category": "model_usage",
                    "summary": "README references GPT-4o and Whisper APIs.",
                    "confidence": "high",
                    "evidence_type": "explicit",
                    "source_refs": [{"path": "README.md", "source_kind": "readme"}],
                }
            ],
        },
        "derived_observations": {
            "detected_risk_surfaces": ["file_upload", "external_model_dependency"],
            "open_questions": ["Authentication requirements are not described in the README."],
        },
    }

    system_case = SystemCase.model_validate(payload)

    assert system_case.target_type == "repository"
    assert system_case.capability_profile.model_backends == ["gpt-4o", "whisper"]
    assert system_case.evidence.inspected_files[0].path == "README.md"
