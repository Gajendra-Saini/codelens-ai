from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.generation.llm import LLMService


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Keep startup lightweight.
    # Heavy ML services are initialized lazily when needed.

    app.state.llm_service = LLMService()

    app.state.repository_indexing_service = None
    app.state.retrieval_service = None

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