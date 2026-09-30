# This file defines the data models used throughout the application.
# These models store the important information about repositories,
# files, code structures, and chunks that we need during indexing
# and later during retrieval.

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

class CodeStructure(BaseModel):
    type: str
    name: str
    parameters: list[str]
    start_line: int
    end_line: int
    parent: str | None = None
    docstring: str | None = None

class CodeChunk(BaseModel):
    content: str
    path: Path
    language: str
    structure_type: str
    name: str
    parent: str | None = None
    start_line: int
    end_line: int