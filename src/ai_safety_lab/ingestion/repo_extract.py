from __future__ import annotations

from pathlib import Path

from ai_safety_lab.schemas import (
    CapabilityProfile,
    DerivedObservations,
    EvidenceBundle,
    EvidenceExcerpt,
    EvidenceItem,
    EvidenceSignal,
    InspectedFile,
    SecurityPosture,
    SourceKind,
    SourceMetadata,
    SourceRef,
)

from .models import FetchedRepository, IntakeLogEntry, RepoExtractionResult


PRIORITY_FILES = [
    "README.md",
    ".env.example",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "Dockerfile",
    "docker-compose.yml",
    "setup.sh",
    "Makefile",
    "app.py",
    "main.py",
]
KEYWORDS = [
    "openai",
    "whisper",
    "gemini",
    "anthropic",
    "flask",
    "fastapi",
    "streamlit",
    "upload",
    "file",
    "pdf",
    "auth",
    "login",
    "session",
    "secret",
    "token",
    "ffmpeg",
    "report",
    "export",
    "transcribe",
]
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".toml",
    ".json",
    ".yml",
    ".yaml",
    ".sh",
    ".html",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".css",
}
MAX_FILE_SIZE = 200_000
MAX_CANDIDATE_FILES = 40


def _log(logs: list[IntakeLogEntry], level: str, message: str, details: str | None = None) -> None:
    logs.append(IntakeLogEntry(level=level, message=message, details=details))


def _source_kind_for(path: Path) -> SourceKind:
    lowered = path.name.lower()
    if lowered == "readme.md":
        return "readme"
    if lowered.startswith(".env") or path.suffix in {".toml", ".yml", ".yaml", ".json"}:
        return "config"
    if path.suffix in {".py", ".js", ".ts", ".tsx", ".jsx", ".html"}:
        return "code"
    return "other"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _iter_repo_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part.startswith(".git") for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in PRIORITY_FILES:
            continue
        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                continue
        except OSError:
            continue
        files.append(path)
    return files


def discover_relevant_files(root: Path) -> list[Path]:
    all_files = _iter_repo_files(root)
    priority_hits: list[Path] = []
    keyword_hits: list[Path] = []
    seen: set[Path] = set()

    for relative_name in PRIORITY_FILES:
        path = root / relative_name
        if path.exists() and path.is_file():
            priority_hits.append(path)
            seen.add(path)

    for path in all_files:
        if path in seen:
            continue
        text = _read_text(path).lower()
        if any(keyword in text for keyword in KEYWORDS):
            keyword_hits.append(path)
            seen.add(path)

    remaining = [path for path in all_files if path not in seen]
    candidates = priority_hits + keyword_hits + remaining
    return candidates[:MAX_CANDIDATE_FILES]


def _line_refs(path: Path, lines: list[str], needle: str) -> list[SourceRef]:
    refs: list[SourceRef] = []
    for index, line in enumerate(lines, start=1):
        if needle in line.lower():
            refs.append(
                SourceRef(
                    path=str(path),
                    line_start=index,
                    line_end=index,
                    source_kind=_source_kind_for(path),
                )
            )
    return refs[:3]


def _append_unique(values: list[str], items: list[str]) -> None:
    for item in items:
        if item not in values:
            values.append(item)


def extract_repository_signals(repository: FetchedRepository) -> RepoExtractionResult:
    logs: list[IntakeLogEntry] = []
    candidates = discover_relevant_files(repository.local_path)
    _log(logs, "info", f"Inspected {len(candidates)} candidate files.", details=repository.fetch_method)

    source_metadata = SourceMetadata()
    capability_profile = CapabilityProfile()
    security_posture = SecurityPosture()
    evidence = EvidenceBundle()
    derived = DerivedObservations()

    auth_refs: list[SourceRef] = []
    secret_refs: list[SourceRef] = []
    logging_refs: list[SourceRef] = []
    safety_refs: list[SourceRef] = []
    model_refs: list[SourceRef] = []
    upload_refs: list[SourceRef] = []
    output_refs: list[SourceRef] = []
    requirements_refs: list[SourceRef] = []
    notable_excerpts: list[EvidenceExcerpt] = []

    for path in candidates:
        relative_path = path.relative_to(repository.local_path)
        evidence.inspected_files.append(
            InspectedFile(
                path=str(relative_path),
                file_type=path.suffix.lstrip(".") or "text",
                relevance_reason="priority_or_keyword_match",
            )
        )

        text = _read_text(path)
        lines = text.splitlines()
        lowered = text.lower()

        if path.suffix == ".py":
            _append_unique(source_metadata.languages, ["Python"])
        if path.suffix in {".js", ".jsx"}:
            _append_unique(source_metadata.languages, ["JavaScript"])
        if path.suffix in {".ts", ".tsx"}:
            _append_unique(source_metadata.languages, ["TypeScript"])
        if path.name in {"app.py", "main.py"}:
            _append_unique(source_metadata.entrypoints, [str(relative_path)])

        if "flask" in lowered:
            _append_unique(source_metadata.frameworks, ["Flask"])
        if "fastapi" in lowered:
            _append_unique(source_metadata.frameworks, ["FastAPI"])
        if "streamlit" in lowered:
            _append_unique(source_metadata.frameworks, ["Streamlit"])

        if path.name == "requirements.txt":
            deps = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
            _append_unique(source_metadata.dependencies, deps[:15])
            requirements_refs.extend(_line_refs(relative_path, lines, "==") or [SourceRef(path=str(relative_path), source_kind="config")])
        elif path.name == "pyproject.toml":
            for line in lines:
                striped = line.strip()
                if striped.startswith('"') and striped.endswith('",'):
                    _append_unique(source_metadata.dependencies, [striped.strip('",')])
        elif path.name == "package.json":
            _append_unique(source_metadata.dependencies, ["package.json present"])

        if path.name.startswith(".env"):
            for line in lines:
                striped = line.strip()
                if striped and "=" in striped and not striped.startswith("#"):
                    env_name = striped.split("=", 1)[0].strip()
                    _append_unique(source_metadata.environment_variables, [env_name])

        if "openai" in lowered or "gpt-4o" in lowered:
            _append_unique(capability_profile.model_backends, ["openai"])
            model_refs.extend(_line_refs(relative_path, lines, "openai"))
        if "whisper" in lowered:
            _append_unique(capability_profile.model_backends, ["whisper"])
            model_refs.extend(_line_refs(relative_path, lines, "whisper"))
        if "gemini" in lowered:
            _append_unique(capability_profile.model_backends, ["gemini"])
        if "anthropic" in lowered or "claude" in lowered:
            _append_unique(capability_profile.model_backends, ["anthropic"])

        if "upload" in lowered or "file" in lowered:
            _append_unique(derived.detected_risk_surfaces, ["file_upload"])
            upload_refs.extend(_line_refs(relative_path, lines, "upload"))
        if "audio" in lowered:
            _append_unique(capability_profile.media_inputs, ["audio"])
        if "video" in lowered:
            _append_unique(capability_profile.media_inputs, ["video"])
        if "pdf" in lowered or "docx" in lowered or "text" in lowered:
            _append_unique(capability_profile.media_inputs, ["text"])
        if "transcrib" in lowered:
            _append_unique(capability_profile.tool_capabilities, ["transcription"])
        if "word cloud" in lowered:
            _append_unique(capability_profile.output_capabilities, ["word_cloud"])
        if "pdf export" in lowered or ("pdf" in lowered and "download" in lowered):
            _append_unique(capability_profile.output_capabilities, ["pdf_export"])
            output_refs.extend(_line_refs(relative_path, lines, "pdf"))
        if "report" in lowered:
            _append_unique(capability_profile.output_capabilities, ["analysis_report"])
            output_refs.extend(_line_refs(relative_path, lines, "report"))
        if "session" in lowered or "memory" in lowered:
            _append_unique(capability_profile.statefulness_signals, ["session_state"])
        if "secret_key" in lowered or "secret" in lowered:
            secret_refs.extend(_line_refs(relative_path, lines, "secret"))
        if "auth" in lowered or "login" in lowered:
            auth_refs.extend(_line_refs(relative_path, lines, "auth"))
        if "logging" in lowered or "logger" in lowered:
            logging_refs.extend(_line_refs(relative_path, lines, "logging"))
        if "moderation" in lowered or "safety" in lowered or "guardrail" in lowered:
            safety_refs.extend(_line_refs(relative_path, lines, "safety"))

        if len(notable_excerpts) < 8:
            for keyword in ("openai", "whisper", "upload", "auth", "report"):
                refs = _line_refs(relative_path, lines, keyword)
                if refs:
                    ref = refs[0]
                    excerpt_line = lines[(ref.line_start or 1) - 1][:240]
                    notable_excerpts.append(
                        EvidenceExcerpt(
                            source_ref=ref,
                            excerpt=excerpt_line,
                            note=f"Matched keyword '{keyword}'",
                        )
                    )
                    break

    if source_metadata.frameworks:
        evidence.evidence_items.append(
            EvidenceItem(
                category="framework_detection",
                summary=f"Detected frameworks: {', '.join(source_metadata.frameworks)}.",
                confidence="high",
                evidence_type="explicit",
                source_refs=[SourceRef(path=item.path, source_kind="code") for item in evidence.inspected_files[:3]],
            )
        )
    if capability_profile.model_backends:
        evidence.evidence_items.append(
            EvidenceItem(
                category="model_usage",
                summary=f"Detected model/backend usage: {', '.join(capability_profile.model_backends)}.",
                confidence="high",
                evidence_type="explicit",
                source_refs=model_refs[:3],
            )
        )
    if upload_refs:
        evidence.evidence_items.append(
            EvidenceItem(
                category="upload_surface",
                summary="File or media upload surface detected in reviewed files.",
                confidence="medium",
                evidence_type="explicit",
                source_refs=upload_refs[:3],
            )
        )
    if output_refs:
        evidence.evidence_items.append(
            EvidenceItem(
                category="reporting_output",
                summary=f"Detected output/reporting capabilities: {', '.join(capability_profile.output_capabilities)}.",
                confidence="medium",
                evidence_type="explicit",
                source_refs=output_refs[:3],
            )
        )
    if source_metadata.dependencies:
        evidence.evidence_items.append(
            EvidenceItem(
                category="dependency_setup",
                summary="Dependency manifest or setup files were found.",
                confidence="medium",
                evidence_type="explicit",
                source_refs=requirements_refs[:3],
            )
        )

    security_posture.authentication_signals.append(
        EvidenceSignal(
            label="authentication_layer",
            status="present" if auth_refs else "unclear",
            summary=(
                "Authentication- or login-related language appears in reviewed files."
                if auth_refs
                else "No explicit authentication layer was found in the reviewed files."
            ),
            source_refs=auth_refs[:3],
        )
    )
    security_posture.secret_handling_signals.append(
        EvidenceSignal(
            label="secret_management",
            status="present" if secret_refs or source_metadata.environment_variables else "unclear",
            summary=(
                "Environment-variable or secret-handling signals were detected."
                if secret_refs or source_metadata.environment_variables
                else "No explicit secret-management signals were found in the reviewed files."
            ),
            source_refs=(secret_refs[:3] or [SourceRef(path=".env.example", source_kind="config")] if source_metadata.environment_variables else []),
        )
    )
    security_posture.logging_signals.append(
        EvidenceSignal(
            label="logging_visibility",
            status="present" if logging_refs else "unclear",
            summary=(
                "Logging-related signals were detected."
                if logging_refs
                else "No explicit logging or audit trail signals were found in the reviewed files."
            ),
            source_refs=logging_refs[:3],
        )
    )
    security_posture.safety_control_signals.append(
        EvidenceSignal(
            label="safety_controls",
            status="present" if safety_refs else "unclear",
            summary=(
                "Safety or moderation-related language was detected."
                if safety_refs
                else "No explicit safety-control language was found in the reviewed files."
            ),
            source_refs=safety_refs[:3],
        )
    )
    security_posture.dependency_risk_signals.append(
        EvidenceSignal(
            label="dependency_manifest",
            status="present" if source_metadata.dependencies else "unclear",
            summary=(
                "Dependency manifests or setup files were detected."
                if source_metadata.dependencies
                else "No dependency manifest was detected in the reviewed files."
            ),
            source_refs=requirements_refs[:3],
        )
    )

    if not auth_refs:
        derived.open_questions.append("Authentication or authorization requirements were not explicit in the reviewed files.")
        _log(logs, "warning", "Authentication signals were unclear.", details=repository.repo_name)
    if not capability_profile.model_backends:
        derived.open_questions.append("Model backend usage could not be determined confidently from the reviewed files.")
        _log(logs, "warning", "Model backend usage was unclear.")
    if not source_metadata.dependencies:
        derived.open_questions.append("Dependency setup requirements were not explicit in the reviewed files.")
        _log(logs, "warning", "Dependency manifests were not detected.")
    if "file_upload" in derived.detected_risk_surfaces:
        _log(logs, "info", "Detected file upload surface.", details=repository.repo_name)
    if capability_profile.output_capabilities:
        _log(logs, "info", "Detected output/reporting capabilities.", details=", ".join(capability_profile.output_capabilities))

    derived.operational_constraints.append("Repository analysis is static and may miss runtime-only controls or behaviors.")
    derived.confidence_notes.append(
        "Signals were extracted deterministically from prioritized files and keyword-matched code paths."
    )

    evidence.notable_excerpts = notable_excerpts
    evidence.raw_summary = (
        f"Repository {repository.owner}/{repository.repo_name} fetched via {repository.fetch_method}. "
        f"Detected frameworks: {', '.join(source_metadata.frameworks) or 'unknown'}. "
        f"Detected model backends: {', '.join(capability_profile.model_backends) or 'unknown'}. "
        f"Risk surfaces: {', '.join(derived.detected_risk_surfaces) or 'none detected'}."
    )

    return RepoExtractionResult(
        repository=repository,
        source_metadata=source_metadata,
        capability_profile=capability_profile,
        security_posture=security_posture,
        evidence=evidence,
        derived_observations=derived,
        intake_logs=logs,
    )
