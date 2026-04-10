from __future__ import annotations

from ai_safety_lab.adapters import system_case_from_case_file
from tests.helpers import sample_case_file


def test_case_file_adapter_preserves_conversation_content() -> None:
    case_file = sample_case_file()

    system_case = system_case_from_case_file(case_file)

    assert system_case.target_type == "conversation"
    assert system_case.case_id == case_file.case_id
    assert system_case.conversation_transcript == case_file.transcript
    assert system_case.tool_logs == case_file.tool_logs
    assert system_case.memory_logs == case_file.memory_logs
    assert system_case.capability_profile.model_backends == [case_file.target_model]
    assert system_case.evidence.raw_summary is not None
    assert system_case.derived_observations.confidence_notes
