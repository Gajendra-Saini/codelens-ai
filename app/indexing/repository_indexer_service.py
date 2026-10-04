# This file handles the indexing of an entire repository.
# It connects the loader, chunker, embedding, metadata, and Qdrant services.


from app.embeddings.service import EmbeddingService
from app.indexing.indexer import Indexer
from app.indexing.metadata import IndexMetadataStore
from app.indexing.repository_indexer import RepositoryIndexer
from app.repositories.loader import RepositoryLoader
from app.repositories.text_chunker import TextChunker
from app.vectorstore.qdrant import QdrantVectorStore


class RepositoryIndexingService:

    def __init__(
        self,
        repository_loader=None,
        repository_indexer=None,
        embedding_service=None,
    ):
        # Repository loader
        self.repository_loader = (
            repository_loader
            or RepositoryLoader(
                storage_dir="storage/repositories"
            )
        )

        # Allow dependency injection for testing later
        if repository_indexer is not None:
            self.repository_indexer = repository_indexer
            return

        # Metadata
        metadata_store = IndexMetadataStore(
            metadata_path="storage/index_metadata.json"
        )

        # Incremental indexing logic
        indexer = Indexer(
            metadata_store=metadata_store
        )

        # Text chunking
        chunker = TextChunker()

        # Embeddings
        embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        # Qdrant
        vector_store = QdrantVectorStore(
            collection_name="codelens_chunks"
        )

        # File-level indexing pipeline
        self.repository_indexer = RepositoryIndexer(
            indexer=indexer,
            chunker=chunker,
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

    def index_repository(self, repo_url: str):

        # 1. Clone or update repository
        repository = self.repository_loader.clone(
            repo_url
        )

        # 2. Discover supported files
        file_paths = self.repository_loader.discover_files(
            repository
        )

        # 3. Convert paths → CodeFile objects
        code_files = self.repository_loader.build_code_files(
            repository,
            file_paths,
        )

        # 4. Keep track of files currently present
        current_file_paths = set()

        results = []

        # 5. Index each file
        for code_file in code_files:

            file_path = str(code_file.path)

            current_file_paths.add(file_path)

            result = self.repository_indexer.index_file(
                repository_id=str(repository.id),
                code_file=code_file,
            )

            results.append(result)

        # 6. Remove files that disappeared from repository
        deleted_files = (
            self.repository_indexer.remove_deleted_files(
                repository_id=str(repository.id),
                current_file_paths=current_file_paths,
            )
        )

        # 7. Return summary
        return {
            "repository_id": str(repository.id),
            "files_found": len(code_files),
            "results": results,
            "deleted_files": list(deleted_files),
        }