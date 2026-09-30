import pytest
import subprocess

from pathlib import Path
from unittest.mock import patch

from app.repositories.loader import (
    RepositoryLoader,
    RepositoryLoadError,
)
from app.repositories.models import Repository

def test_same_repository_gets_same_id(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    url = "https://github.com/Gajendra-Saini/testingrag"

    id1 = loader._get_repository_id(url)
    id2 = loader._get_repository_id(url)

    assert id1 == id2

def test_different_repositories_get_different_ids(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    url1 = "https://github.com/Gajendra-Saini/testingrag"
    url2 = "https://github.com/Gajendra-Saini/another-repo"

    id1 = loader._get_repository_id(url1)
    id2 = loader._get_repository_id(url2)

    assert id1 != id2

def test_repository_url_normalization(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    url1 = "https://github.com/Gajendra-Saini/testingrag"
    url2 = "https://github.com/Gajendra-Saini/testingrag/"
    url3 = "https://github.com/Gajendra-Saini/testingrag.git"

    id1 = loader._get_repository_id(url1)
    id2 = loader._get_repository_id(url2)
    id3 = loader._get_repository_id(url3)

    assert id1 == id2
    assert id1 == id3

def test_invalid_repository_url_raises_error(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    invalid_url = "https://github.com/Gajendra-Saini"

    with pytest.raises(RepositoryLoadError):
        loader.clone(invalid_url)
def test_clone_calls_git_clone(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repo_url = "https://github.com/Gajendra-Saini/testingrag"

    with patch("app.repositories.loader.subprocess.run") as mock_run:

        mock_run.return_value.returncode = 0

        repository = loader.clone(repo_url)

    mock_run.assert_called_once_with(
        [
            "git",
            "clone",
            repo_url,
            str(repository.path),
        ],
        capture_output=True,
        text=True,
    )

    assert repository.id == loader._get_repository_id(repo_url)

def test_existing_repository_uses_git_pull(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repo_url = "https://github.com/Gajendra-Saini/testingrag"

    repository_id = loader._get_repository_id(repo_url)
    repository_path = tmp_path / str(repository_id)

    repository_path.mkdir()

    # Make the directory look like an existing Git repository
    (repository_path / ".git").mkdir()

    with patch("app.repositories.loader.subprocess.run") as mock_run:

        mock_run.return_value.returncode = 0

        repository = loader.clone(repo_url)

    mock_run.assert_called_once_with(
        [
            "git",
            "-C",
            str(repository_path),
            "pull",
            "--ff-only",
        ],
        capture_output=True,
        text=True,
    )

    assert repository.id == repository_id
    assert repository.path == repository_path

def test_existing_non_git_directory_raises_error(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repo_url = "https://github.com/Gajendra-Saini/testingrag"

    repository_id = loader._get_repository_id(repo_url)
    repository_path = tmp_path / str(repository_id)

    # Directory exists, but there is no .git directory
    repository_path.mkdir()

    with pytest.raises(RepositoryLoadError, match="not a Git repository"):
        loader.clone(repo_url)

def test_discover_files_recursively(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repository_path = tmp_path / "repo"

    (repository_path / "docs").mkdir(parents=True)
    (repository_path / "src").mkdir(parents=True)

    (repository_path / "auth.txt").write_text(
        "authentication",
        encoding="utf-8",
    )

    (repository_path / "docs" / "database.txt").write_text(
        "database",
        encoding="utf-8",
    )

    (repository_path / "src" / "payment.txt").write_text(
        "payment",
        encoding="utf-8",
    )

    (repository_path / "README.md").write_text(
        "readme",
        encoding="utf-8",
    )

    repository = Repository(
        id=loader._get_repository_id(
            "https://github.com/Gajendra-Saini/testingrag"
        ),
        path=repository_path,
    )

    discovered_files = loader.discover_files(repository)

    discovered_relative_paths = {
        path.relative_to(repository_path)
        for path in discovered_files
    }

    assert discovered_relative_paths == {
        Path("auth.txt"),
        Path("docs/database.txt"),
        Path("src/payment.txt"),
    }
def test_discover_files_ignores_directories(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repository_path = tmp_path / "repo"

    (repository_path / ".git").mkdir(parents=True)
    (repository_path / "__pycache__").mkdir(parents=True)
    (repository_path / ".venv").mkdir(parents=True)
    (repository_path / "node_modules").mkdir(parents=True)
    (repository_path / "docs").mkdir(parents=True)

    (repository_path / "valid.txt").write_text(
        "valid file",
        encoding="utf-8",
    )

    (repository_path / ".git" / "config.txt").write_text(
        "should be ignored",
        encoding="utf-8",
    )

    (repository_path / "__pycache__" / "cache.txt").write_text(
        "should be ignored",
        encoding="utf-8",
    )

    (repository_path / ".venv" / "environment.txt").write_text(
        "should be ignored",
        encoding="utf-8",
    )

    (repository_path / "node_modules" / "package.txt").write_text(
        "should be ignored",
        encoding="utf-8",
    )

    (repository_path / "docs" / "guide.txt").write_text(
        "should be included",
        encoding="utf-8",
    )

    repository = Repository(
        id=loader._get_repository_id(
            "https://github.com/Gajendra-Saini/testingrag"
        ),
        path=repository_path,
    )

    discovered_files = loader.discover_files(repository)

    discovered_relative_paths = {
        path.relative_to(repository_path)
        for path in discovered_files
    }

    assert discovered_relative_paths == {
        Path("valid.txt"),
        Path("docs/guide.txt"),
    }
def test_discover_files_is_case_insensitive(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repository_path = tmp_path / "repo"
    repository_path.mkdir()

    (repository_path / "lower.txt").write_text(
        "lowercase",
        encoding="utf-8",
    )

    (repository_path / "upper.TXT").write_text(
        "uppercase",
        encoding="utf-8",
    )

    repository = Repository(
        id=loader._get_repository_id(
            "https://github.com/Gajendra-Saini/testingrag"
        ),
        path=repository_path,
    )

    discovered_files = loader.discover_files(repository)

    discovered_names = {
        path.name
        for path in discovered_files
    }

    assert discovered_names == {
        "lower.txt",
        "upper.TXT",
    }
def test_discover_files_ignores_unsupported_extensions(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repository_path = tmp_path / "repo"
    repository_path.mkdir()

    (repository_path / "valid.txt").write_text(
        "valid",
        encoding="utf-8",
    )

    (repository_path / "script.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )

    (repository_path / "readme.md").write_text(
        "# README",
        encoding="utf-8",
    )

    (repository_path / "data.json").write_text(
        '{"name": "test"}',
        encoding="utf-8",
    )

    repository = Repository(
        id=loader._get_repository_id(
            "https://github.com/Gajendra-Saini/testingrag"
        ),
        path=repository_path,
    )

    discovered_files = loader.discover_files(repository)

    discovered_names = {
        path.name
        for path in discovered_files
    }

    assert discovered_names == {
        "valid.txt",
    }
def test_build_code_file(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repository_path = tmp_path / "repo"
    repository_path.mkdir()

    file_path = repository_path / "auth.txt"

    content = "User authentication logic\nSecond line."

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    repository = Repository(
        id=loader._get_repository_id(
            "https://github.com/Gajendra-Saini/testingrag"
        ),
        path=repository_path,
    )

    code_file = loader.build_code_file(
        repository,
        file_path,
    )

    assert code_file.repository_id == repository.id
    assert code_file.path == Path("auth.txt")
    assert code_file.language == "text"
    assert code_file.content == content
    assert code_file.size == file_path.stat().st_size
def test_build_code_file_preserves_nested_relative_path(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repository_path = tmp_path / "repo"
    docs_path = repository_path / "docs"

    docs_path.mkdir(parents=True)

    file_path = docs_path / "database.txt"

    file_path.write_text(
        "database documentation",
        encoding="utf-8",
    )

    repository = Repository(
        id=loader._get_repository_id(
            "https://github.com/Gajendra-Saini/testingrag"
        ),
        path=repository_path,
    )

    code_file = loader.build_code_file(
        repository,
        file_path,
    )

    assert code_file.path == Path("docs/database.txt")
def test_build_code_files(tmp_path):

    loader = RepositoryLoader(
        storage_dir=tmp_path
    )

    repository_path = tmp_path / "repo"

    repository_path.mkdir()

    auth_file = repository_path / "auth.txt"
    payment_file = repository_path / "payment.txt"

    auth_file.write_text(
        "authentication logic",
        encoding="utf-8",
    )

    payment_file.write_text(
        "payment logic",
        encoding="utf-8",
    )

    repository = Repository(
        id=loader._get_repository_id(
            "https://github.com/Gajendra-Saini/testingrag"
        ),
        path=repository_path,
    )

    file_paths = [
        auth_file,
        payment_file,
    ]

    code_files = loader.build_code_files(
        repository,
        file_paths,
    )

    assert len(code_files) == 2

    assert code_files[0].path == Path("auth.txt")
    assert code_files[0].content == "authentication logic"

    assert code_files[1].path == Path("payment.txt")
    assert code_files[1].content == "payment logic"

    assert all(
        code_file.repository_id == repository.id
        for code_file in code_files
    )