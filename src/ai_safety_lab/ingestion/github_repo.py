from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from .models import FetchedRepository


class GitHubRepositoryError(ValueError):
    """Raised when a GitHub repository cannot be normalized or fetched."""


def normalize_github_repo_url(repo_url: str) -> tuple[str, str, str]:
    parsed = urlparse(repo_url.strip())
    if parsed.scheme not in {"http", "https"} or parsed.netloc != "github.com":
        raise GitHubRepositoryError("Only public GitHub repository URLs are supported.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise GitHubRepositoryError("GitHub repository URL must include owner and repository name.")

    owner = parts[0]
    repo_name = parts[1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    normalized_url = f"https://github.com/{owner}/{repo_name}"
    return normalized_url, owner, repo_name


def _clone_repository(repo_url: str, destination: Path) -> Path:
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(destination)],
        check=True,
        capture_output=True,
        text=True,
    )
    return destination


def _download_repository_zip(repo_url: str, destination_root: Path, repo_name: str) -> Path:
    archive_path = destination_root / f"{repo_name}.zip"
    last_error: Exception | None = None
    for branch in ("main", "master"):
        archive_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
        try:
            with urlopen(archive_url) as response:  # noqa: S310 - public GitHub URL validated above
                archive_path.write_bytes(response.read())
            break
        except Exception as exc:  # pragma: no cover - exercised through fallback test via monkeypatch
            last_error = exc
    else:
        raise GitHubRepositoryError(
            f"Failed to download repository archive from {repo_url} using main/master branch conventions: {last_error}"
        ) from last_error

    extract_root = destination_root / f"{repo_name}_zip"
    extract_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(extract_root)

    extracted_dirs = [path for path in extract_root.iterdir() if path.is_dir()]
    if not extracted_dirs:
        raise GitHubRepositoryError("Downloaded repository archive did not contain an extractable directory.")
    return extracted_dirs[0]


def fetch_public_github_repository(repo_url: str, destination_root: Path | None = None) -> FetchedRepository:
    normalized_url, owner, repo_name = normalize_github_repo_url(repo_url)
    work_root = Path(destination_root or tempfile.mkdtemp(prefix="ai_safety_lab_repo_"))
    work_root.mkdir(parents=True, exist_ok=True)
    clone_path = work_root / repo_name

    try:
        local_path = _clone_repository(normalized_url, clone_path)
        fetch_method = "git"
    except (subprocess.CalledProcessError, FileNotFoundError):
        if clone_path.exists():
            shutil.rmtree(clone_path, ignore_errors=True)
        local_path = _download_repository_zip(normalized_url, work_root, repo_name)
        fetch_method = "zip"

    return FetchedRepository(
        repo_url=normalized_url,
        repo_name=repo_name,
        owner=owner,
        local_path=local_path,
        fetch_method=fetch_method,
    )
