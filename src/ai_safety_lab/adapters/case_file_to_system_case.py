from __future__ import annotations

from ai_safety_lab.schemas import (
    CapabilityProfile,
    CaseFile,
    DerivedObservations,
    EvidenceBundle,
    EvidenceExcerpt,
    EvidenceItem,
    SourceRef,
    SourceMetadata,
    SystemCase,
)


def _transcript_summary(case_file: CaseFile) -> str:
    return (
        f"Conversation case with {len(case_file.transcript)} messages, "
        f"{len(case_file.tool_logs)} tool logs, and {len(case_file.memory_logs)} memory logs."
    )


def _transcript_excerpts(case_file: CaseFile) -> list[EvidenceExcerpt]:
    excerpts: list[EvidenceExcerpt] = []
    for index, message in enumerate(case_file.transcript[:3], start=1):
        excerpts.append(
            EvidenceExcerpt(
                source_ref=SourceRef(
                    path=None,
                    line_start=index,
                    line_end=index,
                    source_kind="conversation",
                ),
                excerpt=message.content,
                note=f"{message.role} message",
            )
        )
    return excerpts


def system_case_from_case_file(case_file: CaseFile) -> SystemCase:
    model_backends = [case_file.target_model] if case_file.target_model else []
    evidence_items = [
        EvidenceItem(
            category="conversation_summary",
            summary=_transcript_summary(case_file),
            confidence="high",
            evidence_type="observed",
            source_refs=[SourceRef(source_kind="conversation")],
        )
    ]

    confidence_notes = [
        "Converted from legacy CaseFile input for backward compatibility.",
    ]
    if not case_file.tool_logs:
        confidence_notes.append("No tool logs were provided in the source case.")
    if not case_file.memory_logs:
        confidence_notes.append("No memory logs were provided in the source case.")

    return SystemCase(
        case_id=case_file.case_id,
        created_at=case_file.created_at,
        target_type="conversation",
        title=case_file.case_id,
        source_label="legacy_case_file",
        description="SystemCase generated from a legacy conversation CaseFile.",
        source_metadata=SourceMetadata(),
        capability_profile=CapabilityProfile(model_backends=model_backends),
        evidence=EvidenceBundle(
            evidence_items=evidence_items,
            notable_excerpts=_transcript_excerpts(case_file),
            raw_summary=_transcript_summary(case_file),
        ),
        derived_observations=DerivedObservations(
            operational_constraints=["Source material is a conversation trace rather than a repository or endpoint."],
            confidence_notes=confidence_notes,
        ),
        conversation_transcript=list(case_file.transcript),
        tool_logs=list(case_file.tool_logs),
        memory_logs=list(case_file.memory_logs),
    )
