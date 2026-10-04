from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

from app.repositories.models import (
    CodeFile,
    Repository,
)


class FakeRepositoryLoader:

    def discover_files(
        self,
        repository,
    ):
        return [
            repository.path / "auth.txt",
        ]

    def build_code_files(
        self,
        repository,
        file_paths,
    ):
        return [
            CodeFile(
                repository_id=repository.id,
                path=Path("auth.txt"),
                language="text",
                content=(
                    "Authentication is handled by "
                    "validate_token()."
                ),
                size=48,
            )
        ]


class FakeEmbeddingService:
    pass


class FakeVectorStore:
    pass


class FakeRetriever:

    def __init__(
        self,
        embedding_service,
        vector_store,
        chunks,
    ):
        self.embedding_service = (
            embedding_service
        )
        self.vector_store = vector_store
        self.chunks = chunks


def test_retrieval_service_loads_chunks():

    from app.retrieval.service import (
        RetrievalService,
    )

    repository = Repository(
        id=uuid4(),
        path=Path("/fake/repository"),
    )

    service = RetrievalService(
        repository_loader=FakeRepositoryLoader(),
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(),
    )

    chunks = service._load_chunks(
        repository
    )

    assert len(chunks) == 1

    assert chunks[0].content == (
        "Authentication is handled by "
        "validate_token()."
    )

    assert chunks[0].path == Path(
        "auth.txt"
    )


def test_retrieval_service_builds_pipeline():

    from app.retrieval.service import (
        RetrievalService,
    )

    repository = Repository(
        id=uuid4(),
        path=Path("/fake/repository"),
    )

    fake_retriever = FakeRetriever(
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(),
        chunks=[],
    )

    service = RetrievalService(
        repository_loader=FakeRepositoryLoader(),
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(),
        retriever=fake_retriever,
    )

    pipeline = service.build_pipeline(
        repository
    )

    assert pipeline is not None

    assert pipeline.retriever is fake_retriever


def test_build_pipeline_reuses_cached_pipeline():

    from app.retrieval.service import (
        RetrievalService,
    )

    repository = Repository(
        id=uuid4(),
        path=Path("/fake/repository"),
    )

    repository_loader = Mock()

    repository_loader.discover_files.return_value = []

    repository_loader.build_code_files.return_value = []

    embedding_service = Mock()
    vector_store = Mock()
    fake_retriever = Mock()

    service = RetrievalService(
        repository_loader=repository_loader,
        embedding_service=embedding_service,
        vector_store=vector_store,
        retriever=fake_retriever,
    )

    first_pipeline = service.build_pipeline(
        repository
    )

    second_pipeline = service.build_pipeline(
        repository
    )

    # The same repository should return
    # the exact same cached pipeline.
    assert first_pipeline is second_pipeline

    # The retriever supplied to the service
    # should be reused.
    assert (
        first_pipeline.retriever
        is fake_retriever
    )

    # Repository loading should happen only
    # during the first pipeline construction.
    repository_loader.discover_files.assert_called_once_with(
        repository
    )

    repository_loader.build_code_files.assert_called_once_with(
        repository,
        [],
    )


def test_invalidate_repository_forces_pipeline_rebuild():

    from app.retrieval.service import (
        RetrievalService,
    )

    repository = Repository(
        id=uuid4(),
        path=Path("/fake/repository"),
    )

    repository_loader = Mock()

    repository_loader.discover_files.return_value = []

    repository_loader.build_code_files.return_value = []

    embedding_service = Mock()
    vector_store = Mock()

    first_retriever = Mock()
    second_retriever = Mock()

    service = RetrievalService(
        repository_loader=repository_loader,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    # Replace the service-level retriever before
    # the first build.
    service.retriever = first_retriever

    first_pipeline = service.build_pipeline(
        repository
    )

    service.invalidate_repository(
        str(repository.id)
    )

    # Give the next pipeline a different retriever
    # so we can prove a new pipeline was created.
    service.retriever = second_retriever

    second_pipeline = service.build_pipeline(
        repository
    )

    # Cache invalidation must force creation
    # of a new pipeline.
    assert first_pipeline is not second_pipeline

    # The retriever should also be different.
    assert (
        first_pipeline.retriever
        is not second_pipeline.retriever
    )

    # Repository loading should happen once
    # before invalidation and once after it.
    assert (
        repository_loader
        .discover_files
        .call_count
        == 2
    )

    assert (
        repository_loader
        .build_code_files
        .call_count
        == 2
    )