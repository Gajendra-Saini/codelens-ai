from pathlib import Path

from fastapi import Depends, Request

from app.api.schemas import QueryRequest
from app.core.exceptions import RepositoryNotFoundError
from app.embeddings.service import EmbeddingService
from app.generation.prompt_builder import PromptBuilder
from app.generation.query_service import QueryService
from app.indexing.repository_indexer_service import (
    RepositoryIndexingService,
)
from app.repositories.models import Repository
from app.retrieval.service import RetrievalService


def get_repository_indexing_service(
    request: Request,
):
    if request.app.state.repository_indexing_service is None:

        embedding_service = EmbeddingService()

        request.app.state.embedding_service = (
            embedding_service
        )

        request.app.state.repository_indexing_service = (
            RepositoryIndexingService(
                embedding_service=embedding_service
            )
        )

    return (
        request
        .app
        .state
        .repository_indexing_service
    )


def get_retrieval_service(
    request: Request,
):
    if request.app.state.retrieval_service is None:

        embedding_service = (
            getattr(
                request.app.state,
                "embedding_service",
                None,
            )
            or EmbeddingService()
        )

        request.app.state.embedding_service = (
            embedding_service
        )

        request.app.state.retrieval_service = (
            RetrievalService(
                embedding_service=embedding_service
            )
        )

    return (
        request
        .app
        .state
        .retrieval_service
    )


def get_llm_service(
    request: Request,
):
    return (
        request
        .app
        .state
        .llm_service
    )


def get_repository(
    request: QueryRequest,
) -> Repository:

    repository_id = request.repository_id

    repository_path = (
        Path("storage/repositories")
        / str(repository_id)
    )

    if not repository_path.exists():

        raise RepositoryNotFoundError(
            f"Repository {repository_id} "
            f"is not indexed."
        )

    return Repository(
        id=repository_id,
        path=repository_path,
    )


def get_query_service(
    request: Request,
    repository: Repository = Depends(
        get_repository
    ),
):

    retrieval_service = (
        get_retrieval_service(request)
    )

    llm_service = (
        get_llm_service(request)
    )

    retrieval_pipeline = (
        retrieval_service.build_pipeline(
            repository
        )
    )

    prompt_builder = PromptBuilder()

    return QueryService(
        retrieval_pipeline=retrieval_pipeline,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )