from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.api.dependencies import (
    get_query_service,
    get_repository_indexing_service,
    get_retrieval_service,
)

from app.api.schemas import (
    QueryRequest,
    RepositoryIndexRequest,
)

from app.core.exceptions import (
    GenerationUnavailableError,
    InvalidRepositoryUrlError,
    RepositoryCloneError,
    RepositoryNotFoundError,
)

from app.generation.query_service import (
    QueryService,
)

from app.indexing.repository_indexer_service import (
    RepositoryIndexingService,
)


router = APIRouter()


@router.post("/repositories/index")
def index_repository(
    request: RepositoryIndexRequest,
    service: RepositoryIndexingService = Depends(
        get_repository_indexing_service
    ),
):
    try:
        result = service.index_repository(
            request.repo_url
        )

        return result

    except InvalidRepositoryUrlError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except RepositoryCloneError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/query")
def query_repository(
    request: QueryRequest,
    query_service: QueryService = Depends(
        get_query_service
    ),
):
    try:
        return query_service.answer(
            request.question
        )

    except RepositoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except GenerationUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc