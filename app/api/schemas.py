from uuid import UUID

from pydantic import BaseModel


class RepositoryIndexRequest(BaseModel):
    repo_url: str


class QueryRequest(BaseModel):
    repository_id: UUID
    question: str