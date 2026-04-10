from __future__ import annotations

from pathlib import Path

from ai_safety_lab.ingestion.models import FetchedRepository
from ai_safety_lab.ingestion.repo_extract import discover_relevant_files, extract_repository_signals


def _make_repo_fixture(root: Path) -> FetchedRepository:
    (root / "README.md").write_text(
        "# VeriMedia\n"
        "Flask app using OpenAI GPT-4o and Whisper APIs.\n"
        "Users can upload text, audio, and video files.\n"
        "Download a PDF report after analysis.\n"
    )
    (root / "requirements.txt").write_text("flask==3.0.0\nopenai==1.0.0\n")
    (root / ".env.example").write_text("OPENAI_API_KEY=\nSECRET_KEY=\n")
    (root / "app.py").write_text(
        "from flask import Flask, request, session\n"
        "app = Flask(__name__)\n"
        "def upload_file():\n"
        "    file = request.files['file']\n"
        "    return file\n"
    )
    return FetchedRepository(
        repo_url="https://github.com/FlashCarrot/VeriMedia",
        repo_name="VeriMedia",
        owner="FlashCarrot",
        local_path=root,
        fetch_method="git",
    )


def test_discover_relevant_files_prioritizes_expected_inputs(tmp_path: Path) -> None:
    repository = _make_repo_fixture(tmp_path)

    files = discover_relevant_files(repository.local_path)
    relative_paths = {str(path.relative_to(repository.local_path)) for path in files}

    assert "README.md" in relative_paths
    assert "requirements.txt" in relative_paths
    assert "app.py" in relative_paths


def test_extract_repository_signals_detects_core_repo_capabilities(tmp_path: Path) -> None:
    repository = _make_repo_fixture(tmp_path)

    result = extract_repository_signals(repository)

    assert "Flask" in result.source_metadata.frameworks
    assert "openai" in result.capability_profile.model_backends
    assert "whisper" in result.capability_profile.model_backends
    assert "file_upload" in result.derived_observations.detected_risk_surfaces
    assert result.evidence.evidence_items
    assert result.evidence.notable_excerpts
