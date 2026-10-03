from pathlib import Path
from uuid import uuid4

from app.repositories.models import Repository, CodeFile


class FakeRepositoryLoader:

    def discover_files(self, repository):
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
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.chunks = chunks


def test_retrieval_service_loads_chunks():

    from app.retrieval.service import RetrievalService

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

    assert chunks[0].path == Path("auth.txt")


def test_retrieval_service_builds_pipeline():

    from app.retrieval.service import RetrievalService

    repository = Repository(
        id=uuid4(),
        path=Path("/fake/repository"),
    )

    service = RetrievalService(
        repository_loader=FakeRepositoryLoader(),
        embedding_service=FakeEmbeddingService(),
        vector_store=FakeVectorStore(),
        retriever=FakeRetriever,
    )

    pipeline = service.build_pipeline(
        repository
    )

    assert pipeline is not None

    assert pipeline.retriever is not None

    assert len(
        pipeline.retriever.chunks
    ) == 1

    assert (
        pipeline.retriever.chunks[0].content
        == "Authentication is handled by "
        "validate_token()."
    )
def test_retrieval_service_builds_pipeline():

    from app.retrieval.service import RetrievalService

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