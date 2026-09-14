from pathlib import Path
from uuid import UUID

from pydantic import BaseModel


class Repository(BaseModel):
    id: UUID
    path: Path


class CodeFile(BaseModel):
    repository_id: UUID
    path: Path
    language: str
    content: str
    size: int