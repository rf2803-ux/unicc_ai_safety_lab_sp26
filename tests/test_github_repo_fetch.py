from __future__ import annotations

from pathlib import Path

import pytest

from ai_safety_lab.ingestion.github_repo import (
    GitHubRepositoryError,
    fetch_public_github_repository,
    normalize_github_repo_url,
)


def test_normalize_github_repo_url_accepts_repo_variants() -> None:
    normalized, owner, repo_name = normalize_github_repo_url(
        "https://github.com/FlashCarrot/VeriMedia/tree/main"
    )

    assert normalized == "https://github.com/FlashCarrot/VeriMedia"
    assert owner == "FlashCarrot"
    assert repo_name == "VeriMedia"


def test_normalize_github_repo_url_rejects_non_github_urls() -> None:
    with pytest.raises(GitHubRepositoryError):
        normalize_github_repo_url("https://example.com/not-github/repo")


def test_fetch_public_github_repository_falls_back_to_zip(tmp_path: Path, monkeypatch) -> None:
    def fake_clone(repo_url: str, destination: Path) -> Path:
        raise FileNotFoundError("git not available")

    def fake_download(repo_url: str, destination_root: Path, repo_name: str) -> Path:
        extracted = destination_root / f"{repo_name}_snapshot"
        extracted.mkdir(parents=True, exist_ok=True)
        (extracted / "README.md").write_text("# Demo repo\n")
        return extracted

    monkeypatch.setattr("ai_safety_lab.ingestion.github_repo._clone_repository", fake_clone)
    monkeypatch.setattr("ai_safety_lab.ingestion.github_repo._download_repository_zip", fake_download)

    fetched = fetch_public_github_repository(
        "https://github.com/FlashCarrot/VeriMedia",
        destination_root=tmp_path,
    )

    assert fetched.fetch_method == "zip"
    assert fetched.local_path.exists()
    assert fetched.repo_name == "VeriMedia"
