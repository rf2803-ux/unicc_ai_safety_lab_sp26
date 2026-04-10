from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from ai_safety_lab.schemas import (
    CapabilityProfile,
    DerivedObservations,
    EvidenceBundle,
    SecurityPosture,
    SourceMetadata,
)


class FetchedRepository(BaseModel):
    repo_url: str
    repo_name: str
    owner: str
    local_path: Path
    fetch_method: Literal["git", "zip"]


class IntakeLogEntry(BaseModel):
    level: Literal["info", "warning", "error"] = "info"
    message: str
    details: str | None = None


class RepoExtractionResult(BaseModel):
    repository: FetchedRepository
    source_metadata: SourceMetadata = Field(default_factory=SourceMetadata)
    capability_profile: CapabilityProfile = Field(default_factory=CapabilityProfile)
    security_posture: SecurityPosture = Field(default_factory=SecurityPosture)
    evidence: EvidenceBundle = Field(default_factory=EvidenceBundle)
    derived_observations: DerivedObservations = Field(default_factory=DerivedObservations)
    intake_logs: list[IntakeLogEntry] = Field(default_factory=list)


RuntimeMode = Literal["auto", "json_api", "simple_web_app"]
DetectedRuntimeMode = Literal["json_api", "simple_web_app", "unknown"]
HttpMethod = Literal["GET", "POST"]


class RuntimeProbeDefinition(BaseModel):
    probe_id: str
    label: str
    prompt: str
    objective: str


class RuntimeProbeConfig(BaseModel):
    url: str
    mode: RuntimeMode = "auto"
    method: HttpMethod = "POST"
    prompt_field: str | None = None
    static_payload: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    notes: str | None = None
    timeout_seconds: float = 10.0
    max_probes: int = 4
    form_field: str | None = None


class RuntimeObservedInteraction(BaseModel):
    interaction_id: str
    probe_label: str
    request_summary: str
    response_summary: str
    status_code: int | None = None
    endpoint_path: str | None = None
    method: str | None = None
    payload_redacted: str | None = None
    response_excerpt: str | None = None
    safety_notes: list[str] = Field(default_factory=list)


class RuntimeProbeResult(BaseModel):
    config: RuntimeProbeConfig
    detected_mode: DetectedRuntimeMode
    interactions: list[RuntimeObservedInteraction] = Field(default_factory=list)
    intake_logs: list[IntakeLogEntry] = Field(default_factory=list)
    source_metadata: SourceMetadata = Field(default_factory=SourceMetadata)
    capability_profile: CapabilityProfile = Field(default_factory=CapabilityProfile)
    security_posture: SecurityPosture = Field(default_factory=SecurityPosture)
    evidence: EvidenceBundle = Field(default_factory=EvidenceBundle)
    derived_observations: DerivedObservations = Field(default_factory=DerivedObservations)
