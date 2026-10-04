# Builds and caches the retrieval pipeline for indexed repositories.

from app.repositories.loader import RepositoryLoader
from app.repositories.text_chunker import TextChunker
from app.embeddings.service import EmbeddingService
from app.vectorstore.qdrant import QdrantVectorStore

from app.retrieval.retriever import Retriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.relevance import RelevanceGate
from app.retrieval.pipeline import RetrievalPipeline

from app.context.builder import ContextBuilder


class RetrievalService:

    def __init__(
        self,
        repository_loader=None,
        embedding_service=None,
        vector_store=None,
        retriever=None,
        reranker=None,
    ):

        self.repository_loader = (
            repository_loader
            or RepositoryLoader(
                storage_dir="storage/repositories"
            )
        )

        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.vector_store = (
            vector_store
            or QdrantVectorStore(
                collection_name="codelens_chunks"
            )
        )

        self.chunker = TextChunker()

        self.retriever = retriever

        self.reranker = (
            reranker
            or CrossEncoderReranker()
        )

        # Cache one retrieval pipeline per repository.
        #
        # repository_id -> RetrievalPipeline
        self._pipeline_cache = {}

    def _load_chunks(self, repository):

        file_paths = (
            self.repository_loader.discover_files(
                repository
            )
        )

        code_files = (
            self.repository_loader.build_code_files(
                repository,
                file_paths,
            )
        )

        chunks = []

        for code_file in code_files:

            chunks.extend(
                self.chunker.create_chunks(
                    code_file
                )
            )

        return chunks

    def build_pipeline(
        self,
        repository,
    ):

        repository_id = str(
            repository.id
        )

        # Reuse an existing pipeline.
        cached_pipeline = (
            self._pipeline_cache.get(
                repository_id
            )
        )

        if cached_pipeline is not None:
            return cached_pipeline

        # Build retrieval state only once.
        chunks = self._load_chunks(
            repository
        )

        retriever = (
            self.retriever
            or Retriever(
                embedding_service=self.embedding_service,
                vector_store=self.vector_store,
                chunks=chunks,
                reranker=self.reranker,
            )
        )

        relevance_gate = RelevanceGate(
            threshold=0.0
        )

        context_builder = ContextBuilder()

        pipeline = RetrievalPipeline(
            retriever=retriever,
            relevance_gate=relevance_gate,
            context_builder=context_builder,
        )

        # Store the completed pipeline.
        self._pipeline_cache[
            repository_id
        ] = pipeline

        return pipeline

    def invalidate_repository(
        self,
        repository_id: str,
    ):
        """
        Remove a repository's cached retrieval
        pipeline so it will be rebuilt on the
        next query.
        """

        self._pipeline_cache.pop(
            str(repository_id),
            None,
        )
def build_pipeline(
    self,
    repository,
):

    repository_id = str(
        repository.id
    )

    cached_pipeline = (
        self._pipeline_cache.get(
            repository_id
        )
    )

    if cached_pipeline is not None:

        print(
            f"Reusing cached retrieval pipeline for "
            f"repository {repository_id}"
        )

        return cached_pipeline

    print(
        f"Building retrieval pipeline for "
        f"repository {repository_id}"
    )

    chunks = self._load_chunks(
        repository
    )

    retriever = (
        self.retriever
        or Retriever(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
            chunks=chunks,
            reranker=self.reranker,
        )
    )

    relevance_gate = RelevanceGate(
        threshold=0.0
    )

    context_builder = ContextBuilder()

    pipeline = RetrievalPipeline(
        retriever=retriever,
        relevance_gate=relevance_gate,
        context_builder=context_builder,
    )

    self._pipeline_cache[
        repository_id
    ] = pipeline

    return pipeline