from pathlib import Path
import subprocess
import uuid
import shutil

from app.repositories.models import Repository
from app.repositories.validator import is_valid_git_url
from app.repositories.models import CodeFile, Repository
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
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".md",
}


class RepositoryLoadError(Exception):
    pass


class RepositoryLoader:

    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def clone(self, repo_url: str):
        if not is_valid_git_url(repo_url):
            raise RepositoryLoadError("Invalid GitHub repository URL")

        repo_id = uuid.uuid4()
        destination_path = self.storage_dir / str(repo_id)

        result = subprocess.run(
            ["git", "clone", repo_url, str(destination_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            shutil.rmtree(destination_path, ignore_errors=True)
            raise RepositoryLoadError(
                f"Failed to clone repository: {result.stderr.strip()}"
            )

        return Repository(
            id=repo_id,
            path=destination_path,
        )

    def discover_files(self, repository: Repository) -> list[Path]:
        files = []

        for path in repository.path.rglob("*"):
            if (
                path.is_file()
                and not any(part in IGNORED_DIRECTORIES for part in path.parts)
                and path.suffix in SUPPORTED_EXTENSIONS
            ):
                files.append(path)

        return files

    def build_code_file(
        self,
        repository: Repository,
        file_path: Path,
    ) -> CodeFile:
        content = file_path.read_text()
        size = file_path.stat().st_size
        language = LANGUAGE_BY_EXTENSION.get(file_path.suffix)

        relative_path = file_path.relative_to(repository.path)

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
            self.build_code_file(repository, file_path)
            for file_path in file_paths
        ]