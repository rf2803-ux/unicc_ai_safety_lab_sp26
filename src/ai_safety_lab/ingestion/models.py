from __future__ import annotations

from pathlib import Path
from typing import Literal

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
