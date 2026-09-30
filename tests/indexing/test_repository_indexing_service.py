from pathlib import Path
from uuid import uuid4
from unittest.mock import Mock

from app.indexing.repository_indexer_service import (
    RepositoryIndexingService,
)
from app.repositories.models import CodeFile, Repository


def create_service():
    repository_loader = Mock()
    repository_indexer = Mock()

    service = RepositoryIndexingService(
        repository_loader=repository_loader,
        repository_indexer=repository_indexer,
    )

    return service, repository_loader, repository_indexer


def create_repository():
    repository_id = uuid4()

    repository = Repository(
        id=repository_id,
        path=Path("/fake/repository"),
    )

    return repository


# ============================================================
# TEST 1
# New repository gets indexed
# ============================================================

def test_new_repository_is_indexed():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    repository_loader.discover_files.return_value = [
        Path("/fake/repository/auth.txt"),
        Path("/fake/repository/database.txt"),
    ]

    code_files = [
        CodeFile(
            repository_id=repository.id,
            path=Path("auth.txt"),
            language="text",
            content="authentication logic",
            size=20,
        ),
        CodeFile(
            repository_id=repository.id,
            path=Path("database.txt"),
            language="text",
            content="database logic",
            size=15,
        ),
    ]

    repository_loader.build_code_files.return_value = code_files

    repository_indexer.index_file.side_effect = [
        {
            "status": "indexed",
            "path": "auth.txt",
            "chunks": 1,
        },
        {
            "status": "indexed",
            "path": "database.txt",
            "chunks": 1,
        },
    ]

    repository_indexer.remove_deleted_files.return_value = set()

    result = service.index_repository(
        "https://github.com/Gajendra-Saini/testingrag"
    )

    assert result["repository_id"] == str(repository.id)

    assert result["files_found"] == 2

    assert len(result["results"]) == 2

    assert result["results"][0]["status"] == "indexed"
    assert result["results"][1]["status"] == "indexed"

    assert result["deleted_files"] == []


# ============================================================
# TEST 2
# Repository loader is called correctly
# ============================================================

def test_repository_is_loaded_with_correct_url():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    repository_loader.discover_files.return_value = []

    repository_loader.build_code_files.return_value = []

    repository_indexer.remove_deleted_files.return_value = set()

    repo_url = "https://github.com/Gajendra-Saini/testingrag"

    service.index_repository(repo_url)

    repository_loader.clone.assert_called_once_with(
        repo_url
    )


# ============================================================
# TEST 3
# Files are discovered from repository
# ============================================================

def test_files_are_discovered_from_repository():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    discovered_files = [
        Path("/fake/repository/auth.txt"),
        Path("/fake/repository/database.txt"),
    ]

    repository_loader.discover_files.return_value = (
        discovered_files
    )

    repository_loader.build_code_files.return_value = []

    repository_indexer.remove_deleted_files.return_value = set()

    service.index_repository(
        "https://github.com/Gajendra-Saini/testingrag"
    )

    repository_loader.discover_files.assert_called_once_with(
        repository
    )


# ============================================================
# TEST 4
# CodeFiles are built correctly
# ============================================================

def test_code_files_are_built_from_discovered_paths():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    discovered_files = [
        Path("/fake/repository/auth.txt"),
        Path("/fake/repository/database.txt"),
    ]

    repository_loader.discover_files.return_value = (
        discovered_files
    )

    repository_loader.build_code_files.return_value = []

    repository_indexer.remove_deleted_files.return_value = set()

    service.index_repository(
        "https://github.com/Gajendra-Saini/testingrag"
    )

    repository_loader.build_code_files.assert_called_once_with(
        repository,
        discovered_files,
    )


# ============================================================
# TEST 5
# Every CodeFile is passed to RepositoryIndexer
# ============================================================

def test_every_code_file_is_indexed():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    repository_loader.discover_files.return_value = []

    code_files = [
        CodeFile(
            repository_id=repository.id,
            path=Path("auth.txt"),
            language="text",
            content="authentication logic",
            size=20,
        ),
        CodeFile(
            repository_id=repository.id,
            path=Path("database.txt"),
            language="text",
            content="database logic",
            size=15,
        ),
    ]

    repository_loader.build_code_files.return_value = (
        code_files
    )

    repository_indexer.index_file.return_value = {
        "status": "indexed",
        "path": "test.txt",
        "chunks": 1,
    }

    repository_indexer.remove_deleted_files.return_value = set()

    service.index_repository(
        "https://github.com/Gajendra-Saini/testingrag"
    )

    assert repository_indexer.index_file.call_count == 2

    repository_indexer.index_file.assert_any_call(
        repository_id=str(repository.id),
        code_file=code_files[0],
    )

    repository_indexer.index_file.assert_any_call(
        repository_id=str(repository.id),
        code_file=code_files[1],
    )


# ============================================================
# TEST 6
# Current file paths are passed to deleted-file cleanup
# ============================================================

def test_current_file_paths_are_passed_to_cleanup():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    repository_loader.discover_files.return_value = []

    code_files = [
        CodeFile(
            repository_id=repository.id,
            path=Path("auth.txt"),
            language="text",
            content="authentication logic",
            size=20,
        ),
        CodeFile(
            repository_id=repository.id,
            path=Path("database.txt"),
            language="text",
            content="database logic",
            size=15,
        ),
    ]

    repository_loader.build_code_files.return_value = (
        code_files
    )

    repository_indexer.remove_deleted_files.return_value = set()

    service.index_repository(
        "https://github.com/Gajendra-Saini/testingrag"
    )

    repository_indexer.remove_deleted_files.assert_called_once_with(
        repository_id=str(repository.id),
        current_file_paths={
            "auth.txt",
            "database.txt",
        },
    )


# ============================================================
# TEST 7
# Deleted files are returned in result
# ============================================================

def test_deleted_files_are_returned():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    repository_loader.discover_files.return_value = []

    repository_loader.build_code_files.return_value = []

    repository_indexer.remove_deleted_files.return_value = {
        "random.txt"
    }

    result = service.index_repository(
        "https://github.com/Gajendra-Saini/testingrag"
    )

    assert result["deleted_files"] == [
        "random.txt"
    ]


# ============================================================
# TEST 8
# Skipped files are still included in results
# ============================================================

def test_skipped_file_is_included_in_results():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    repository_loader.discover_files.return_value = []

    code_file = CodeFile(
        repository_id=repository.id,
        path=Path("auth.txt"),
        language="text",
        content="authentication logic",
        size=20,
    )

    repository_loader.build_code_files.return_value = [
        code_file
    ]

    repository_indexer.index_file.return_value = {
        "status": "skipped",
        "path": "auth.txt",
    }

    repository_indexer.remove_deleted_files.return_value = set()

    result = service.index_repository(
        "https://github.com/Gajendra-Saini/testingrag"
    )

    assert result["results"] == [
        {
            "status": "skipped",
            "path": "auth.txt",
        }
    ]


# ============================================================
# TEST 9
# Empty repository works correctly
# ============================================================

def test_empty_repository():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    repository_loader.discover_files.return_value = []

    repository_loader.build_code_files.return_value = []

    repository_indexer.remove_deleted_files.return_value = set()

    result = service.index_repository(
        "https://github.com/Gajendra-Saini/testingrag"
    )

    assert result["repository_id"] == str(repository.id)

    assert result["files_found"] == 0

    assert result["results"] == []

    assert result["deleted_files"] == []


# ============================================================
# TEST 10
# Multiple files preserve indexing results order
# ============================================================

def test_indexing_results_preserve_file_order():

    service, repository_loader, repository_indexer = (
        create_service()
    )

    repository = create_repository()

    repository_loader.clone.return_value = repository

    repository_loader.discover_files.return_value = []

    code_files = [
        CodeFile(
            repository_id=repository.id,
            path=Path("auth.txt"),
            language="text",
            content="auth",
            size=4,
        ),
        CodeFile(
            repository_id=repository.id,
            path=Path("database.txt"),
            language="text",
            content="database",
            size=8,
        ),
        CodeFile(
            repository_id=repository.id,
            path=Path("payment.txt"),
            language="text",
            content="payment",
            size=7,
        ),
    ]

    repository_loader.build_code_files.return_value = (
        code_files
    )

    repository_indexer.index_file.side_effect = [
        {
            "status": "indexed",
            "path": "auth.txt",
            "chunks": 2,
        },
        {
            "status": "skipped",
            "path": "database.txt",
        },
        {
            "status": "indexed",
            "path": "payment.txt",
            "chunks": 3,
        },
    ]

    repository_indexer.remove_deleted_files.return_value = set()

    result = service.index_repository(
        "https://github.com/Gajendra-Saini/testingrag"
    )

    assert result["results"] == [
        {
            "status": "indexed",
            "path": "auth.txt",
            "chunks": 2,
        },
        {
            "status": "skipped",
            "path": "database.txt",
        },
        {
            "status": "indexed",
            "path": "payment.txt",
            "chunks": 3,
        },
    ]