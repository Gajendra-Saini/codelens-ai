from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.api.routes import router
from app.embeddings.service import EmbeddingService
from app.generation.llm import LLMService
from app.indexing.repository_indexer_service import (
    RepositoryIndexingService,
)
from app.retrieval.service import RetrievalService


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Shared embedding service
    embedding_service = EmbeddingService()

    # Shared LLM service
    llm_service = LLMService()

    # Indexing service
    app.state.repository_indexing_service = (
        RepositoryIndexingService(
            embedding_service=embedding_service
        )
    )

    # Retrieval service
    app.state.retrieval_service = (
        RetrievalService(
            embedding_service=embedding_service
        )
    )

    # LLM service
    app.state.llm_service = llm_service

    yield

    # Application shutdown
    # Cleanup can be added here later.


app = FastAPI(
    title="CodeLens AI",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "CodeLens AI is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


app.include_router(router)