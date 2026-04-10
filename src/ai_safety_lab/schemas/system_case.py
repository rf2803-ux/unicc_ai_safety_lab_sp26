from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from .case_file import MemoryLog, Message, ToolLog


TargetType = Literal["conversation", "repository", "endpoint"]
SignalStatus = Literal["present", "absent", "unclear", "inferred"]
EvidenceConfidence = Literal["high", "medium", "low"]
EvidenceType = Literal["explicit", "inferred", "observed"]
SourceKind = Literal["readme", "code", "config", "runtime", "http", "conversation", "other"]


class SourceRef(BaseModel):
    path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    source_kind: SourceKind = "other"


class InspectedFile(BaseModel):
    path: str
    file_type: str | None = None
    relevance_reason: str | None = None


class EvidenceSignal(BaseModel):
    label: str
    status: SignalStatus
    summary: str
    source_refs: list[SourceRef] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    category: str
    summary: str
    confidence: EvidenceConfidence = "medium"
    evidence_type: EvidenceType = "explicit"
    source_refs: list[SourceRef] = Field(default_factory=list)


class EvidenceExcerpt(BaseModel):
    source_ref: SourceRef
    excerpt: str
    note: str | None = None


class EvidenceBundle(BaseModel):
    inspected_files: list[InspectedFile] = Field(default_factory=list)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    notable_excerpts: list[EvidenceExcerpt] = Field(default_factory=list)
    raw_summary: str | None = None


class SourceMetadata(BaseModel):
    frameworks: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    entrypoints: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    environment_variables: list[str] = Field(default_factory=list)
    deployment_signals: list[str] = Field(default_factory=list)


class CapabilityProfile(BaseModel):
    model_backends: list[str] = Field(default_factory=list)
    media_inputs: list[str] = Field(default_factory=list)
    tool_capabilities: list[str] = Field(default_factory=list)
    output_capabilities: list[str] = Field(default_factory=list)
    statefulness_signals: list[str] = Field(default_factory=list)


class SecurityPosture(BaseModel):
    authentication_signals: list[EvidenceSignal] = Field(default_factory=list)
    authorization_signals: list[EvidenceSignal] = Field(default_factory=list)
    secret_handling_signals: list[EvidenceSignal] = Field(default_factory=list)
    logging_signals: list[EvidenceSignal] = Field(default_factory=list)
    privacy_signals: list[EvidenceSignal] = Field(default_factory=list)
    safety_control_signals: list[EvidenceSignal] = Field(default_factory=list)
    dependency_risk_signals: list[EvidenceSignal] = Field(default_factory=list)


class ObservedInteraction(BaseModel):
    interaction_id: str
    request_summary: str
    response_summary: str
    status_code: int | None = None
    endpoint_path: str | None = None
    method: str | None = None
    payload_redacted: str | None = None
    response_excerpt: str | None = None
    safety_notes: list[str] = Field(default_factory=list)


class DerivedObservations(BaseModel):
    detected_risk_surfaces: list[str] = Field(default_factory=list)
    operational_constraints: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    confidence_notes: list[str] = Field(default_factory=list)


class SystemCase(BaseModel):
    case_id: str
    created_at: datetime
    target_type: TargetType
    title: str
    source_url: str | None = None
    source_label: str | None = None
    description: str | None = None
    source_metadata: SourceMetadata = Field(default_factory=SourceMetadata)
    capability_profile: CapabilityProfile = Field(default_factory=CapabilityProfile)
    security_posture: SecurityPosture = Field(default_factory=SecurityPosture)
    evidence: EvidenceBundle = Field(default_factory=EvidenceBundle)
    observed_interactions: list[ObservedInteraction] = Field(default_factory=list)
    derived_observations: DerivedObservations = Field(default_factory=DerivedObservations)
    conversation_transcript: list[Message] = Field(default_factory=list)
    tool_logs: list[ToolLog] = Field(default_factory=list)
    memory_logs: list[MemoryLog] = Field(default_factory=list)
