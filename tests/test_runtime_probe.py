from __future__ import annotations

import json

from ai_safety_lab.ingestion import RuntimeProbeConfig
from ai_safety_lab.ingestion.runtime_probe import (
    SAFE_DEFAULT_PROBES,
    RuntimeProbeError,
    detect_runtime_mode,
    probe_json_api,
    probe_simple_web_app,
    run_runtime_probe,
)


def test_detect_runtime_mode_prefers_prompt_field_for_json_api() -> None:
    config = RuntimeProbeConfig(url="https://example.com/analyze", prompt_field="input")

    detected = detect_runtime_mode(config)

    assert detected == "json_api"


def test_probe_json_api_collects_safe_interactions(monkeypatch) -> None:
    def fake_request(config, prompt):
        payload = {"input": prompt}
        body = json.dumps({"result": f"handled: {prompt[:12]}"})
        return 200, "application/json", body, payload

    monkeypatch.setattr("ai_safety_lab.ingestion.runtime_probe._request_json_probe", fake_request)
    config = RuntimeProbeConfig(url="https://example.com/analyze", prompt_field="input")

    result = probe_json_api(config, SAFE_DEFAULT_PROBES[:1])

    assert result.detected_mode == "json_api"
    assert len(result.interactions) == 1


def test_run_runtime_probe_json_api_path(monkeypatch) -> None:
    def fake_probe_json_api(config, probes):
        from ai_safety_lab.ingestion.models import RuntimeProbeResult

        return RuntimeProbeResult(config=config, detected_mode="json_api")

    monkeypatch.setattr("ai_safety_lab.ingestion.runtime_probe.probe_json_api", fake_probe_json_api)
    config = RuntimeProbeConfig(url="https://example.com/analyze", prompt_field="prompt")

    result = run_runtime_probe(config)

    assert result.detected_mode == "json_api"


def test_probe_simple_web_app_collects_form_interactions(monkeypatch) -> None:
    html = """
    <html><body>
      <form action="/analyze" method="post">
        <textarea name="message"></textarea>
      </form>
    </body></html>
    """

    monkeypatch.setattr(
        "ai_safety_lab.ingestion.runtime_probe._fetch_html_page",
        lambda config: (200, "text/html", html),
    )

    def fake_submit(config, probe, form):
        payload = {"message": probe.prompt}
        return 200, "text/html", "<div>Request refused for safety reasons.</div>", payload, "https://example.com/analyze", "POST"

    monkeypatch.setattr("ai_safety_lab.ingestion.runtime_probe._submit_simple_form", fake_submit)
    config = RuntimeProbeConfig(url="https://example.com/app", mode="simple_web_app")

    result = probe_simple_web_app(config, SAFE_DEFAULT_PROBES[:1])

    assert result.detected_mode == "simple_web_app"
    assert len(result.interactions) == 1


def test_run_runtime_probe_raises_for_unknown_mode(monkeypatch) -> None:
    monkeypatch.setattr("ai_safety_lab.ingestion.runtime_probe.detect_runtime_mode", lambda config: "unknown")
    config = RuntimeProbeConfig(url="https://example.com")

    try:
        run_runtime_probe(config)
    except RuntimeProbeError as exc:
        assert "could not be classified" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected RuntimeProbeError for unknown runtime mode.")
