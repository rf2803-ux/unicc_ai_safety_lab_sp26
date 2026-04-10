from __future__ import annotations

from pathlib import Path

from ai_safety_lab.ingestion.models import FetchedRepository
from ai_safety_lab.ingestion.repo_extract import extract_repository_signals
from ai_safety_lab.ingestion.repo_to_system_case import system_case_from_repo_extraction


def test_repo_to_system_case_maps_repository_evidence(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "# Demo\n"
        "Streamlit app with OpenAI integration and PDF export.\n"
    )
    (tmp_path / "app.py").write_text("import streamlit as st\nfrom openai import OpenAI\n")
    fetched = FetchedRepository(
        repo_url="https://github.com/example/demo",
        repo_name="demo",
        owner="example",
        local_path=tmp_path,
        fetch_method="zip",
    )

    extracted = extract_repository_signals(fetched)
    system_case = system_case_from_repo_extraction(extracted)

    assert system_case.target_type == "repository"
    assert system_case.source_url == fetched.repo_url
    assert system_case.title == fetched.repo_name
    assert system_case.evidence.raw_summary is not None
