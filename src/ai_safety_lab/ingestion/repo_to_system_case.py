from __future__ import annotations

from datetime import datetime, timezone

from ai_safety_lab.schemas import SystemCase

from .models import RepoExtractionResult


def system_case_from_repo_extraction(extraction: RepoExtractionResult) -> SystemCase:
    repository = extraction.repository
    return SystemCase(
        case_id=f"repo_{repository.owner}_{repository.repo_name}",
        created_at=datetime.now(timezone.utc),
        target_type="repository",
        title=repository.repo_name,
        source_url=repository.repo_url,
        source_label=f"{repository.owner}/{repository.repo_name}",
        description=extraction.evidence.raw_summary,
        source_metadata=extraction.source_metadata,
        capability_profile=extraction.capability_profile,
        security_posture=extraction.security_posture,
        evidence=extraction.evidence,
        derived_observations=extraction.derived_observations,
    )
