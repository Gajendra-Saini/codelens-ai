# This class handles cloning/updating repositories,
# discovering supported files recursively,
# and converting files into CodeFile objects.

from pathlib import Path
import subprocess
import shutil
from urllib.parse import urlparse, urlunparse
from uuid import UUID, uuid5

from app.repositories.models import CodeFile, Repository
from app.repositories.validator import is_valid_git_url
from app.repositories.languages import LANGUAGE_BY_EXTENSION


IGNORED_DIRECTORIES = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".pytest_cache",
}


SUPPORTED_EXTENSIONS = {
    ".txt",
}


class RepositoryLoadError(Exception):
    pass


class RepositoryLoader:

    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _normalize_repo_url(self, repo_url: str) -> str:
        parsed = urlparse(repo_url)

        path = parsed.path.strip("/")

        if path.endswith(".git"):
            path = path[:-4]

        return urlunparse(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                f"/{path}",
                "",
                "",
                "",
            )
        )

    def _get_repository_id(self, repo_url: str) -> UUID:
        normalized_url = self._normalize_repo_url(repo_url)

        return uuid5(
            UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"),
            normalized_url,
        )

    def clone(self, repo_url: str):

        if not is_valid_git_url(repo_url):
            raise RepositoryLoadError(
                "Invalid GitHub repository URL"
            )

        repo_id = self._get_repository_id(repo_url)

        destination_path = self.storage_dir / str(repo_id)

        # Repository already exists locally
        if destination_path.exists():

            if not (destination_path / ".git").exists():
                raise RepositoryLoadError(
                    f"Repository directory exists but is not "
                    f"a Git repository: {destination_path}"
                )

            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(destination_path),
                    "pull",
                    "--ff-only",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise RepositoryLoadError(
                    f"Failed to update repository: "
                    f"{result.stderr.strip()}"
                )

        # Repository does not exist locally
        else:

            result = subprocess.run(
                [
                    "git",
                    "clone",
                    repo_url,
                    str(destination_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:

                shutil.rmtree(
                    destination_path,
                    ignore_errors=True,
                )

                raise RepositoryLoadError(
                    f"Failed to clone repository: "
                    f"{result.stderr.strip()}"
                )

        return Repository(
            id=repo_id,
            path=destination_path,
        )

    def discover_files(
        self,
        repository: Repository,
    ) -> list[Path]:

        files = []

        for path in repository.path.rglob("*"):

            if (
                path.is_file()
                and not any(
                    part in IGNORED_DIRECTORIES
                    for part in path.parts
                )
                and path.suffix.lower()
                in SUPPORTED_EXTENSIONS
            ):
                files.append(path)

        return files

    def build_code_file(
        self,
        repository: Repository,
        file_path: Path,
    ) -> CodeFile:

        content = file_path.read_text(
            encoding="utf-8"
        )

        size = file_path.stat().st_size

        language = LANGUAGE_BY_EXTENSION.get(
            file_path.suffix.lower()
        )

        relative_path = file_path.relative_to(
            repository.path
        )

        return CodeFile(
            repository_id=repository.id,
            path=relative_path,
            language=language,
            content=content,
            size=size,
        )

    def build_code_files(
        self,
        repository: Repository,
        file_paths: list[Path],
    ) -> list[CodeFile]:

        return [
            self.build_code_file(
                repository,
                file_path,
            )
            for file_path in file_paths
        ]