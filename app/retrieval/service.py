# Builds the retrieval pipeline for an indexed repository.

from app.repositories.loader import RepositoryLoader
from app.repositories.text_chunker import TextChunker
from app.embeddings.service import EmbeddingService
from app.vectorstore.qdrant import QdrantVectorStore

from app.retrieval.retriever import Retriever
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

        chunks = self._load_chunks(
            repository
        )

        retriever = (
            self.retriever
            or Retriever(
                embedding_service=self.embedding_service,
                vector_store=self.vector_store,
                chunks=chunks,
            )
        )

        relevance_gate = RelevanceGate(
            threshold=0.0
        )

        context_builder = ContextBuilder()

        return RetrievalPipeline(
            retriever=retriever,
            relevance_gate=relevance_gate,
            context_builder=context_builder,
        )