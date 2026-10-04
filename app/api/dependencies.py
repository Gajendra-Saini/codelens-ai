from pathlib import Path

from fastapi import Depends, Request

from app.api.schemas import QueryRequest
from app.core.exceptions import (
    RepositoryNotFoundError,
)
from app.generation.prompt_builder import PromptBuilder
from app.generation.query_service import QueryService
from app.repositories.models import Repository


def get_repository_indexing_service(
    request: Request,
):

    return (
        request
        .app
        .state
        .repository_indexing_service
    )


def get_retrieval_service(
    request: Request,
):

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
        request
        .app
        .state
        .retrieval_service
    )

    llm_service = (
        request
        .app
        .state
        .llm_service
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