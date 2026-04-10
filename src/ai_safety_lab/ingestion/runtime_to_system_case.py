from __future__ import annotations

from datetime import datetime, timezone

from ai_safety_lab.schemas import ObservedInteraction, SystemCase

from .models import RuntimeProbeResult


def system_case_from_runtime_probe(probe_result: RuntimeProbeResult) -> SystemCase:
    config = probe_result.config
    return SystemCase(
        case_id=f"runtime_{probe_result.detected_mode}_{hash(config.url) & 0xFFFF:x}",
        created_at=datetime.now(timezone.utc),
        target_type="endpoint",
        title=config.url,
        source_url=config.url,
        source_label=probe_result.detected_mode,
        description=probe_result.evidence.raw_summary,
        source_metadata=probe_result.source_metadata,
        capability_profile=probe_result.capability_profile,
        security_posture=probe_result.security_posture,
        evidence=probe_result.evidence,
        observed_interactions=[
            ObservedInteraction(
                interaction_id=item.interaction_id,
                request_summary=item.request_summary,
                response_summary=item.response_summary,
                status_code=item.status_code,
                endpoint_path=item.endpoint_path,
                method=item.method,
                payload_redacted=item.payload_redacted,
                response_excerpt=item.response_excerpt,
                safety_notes=item.safety_notes,
            )
            for item in probe_result.interactions
        ],
        derived_observations=probe_result.derived_observations,
    )
