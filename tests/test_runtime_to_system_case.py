from __future__ import annotations

from ai_safety_lab.ingestion.models import RuntimeProbeConfig, RuntimeProbeResult
from ai_safety_lab.ingestion.runtime_to_system_case import system_case_from_runtime_probe


def test_runtime_probe_maps_into_system_case() -> None:
    probe_result = RuntimeProbeResult(
        config=RuntimeProbeConfig(url="https://example.com/api", prompt_field="input"),
        detected_mode="json_api",
    )

    system_case = system_case_from_runtime_probe(probe_result)

    assert system_case.target_type == "endpoint"
    assert system_case.source_url == "https://example.com/api"
    assert system_case.source_label == "json_api"
