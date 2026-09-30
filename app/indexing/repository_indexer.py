# This file handles indexing of individual files.
# It checks for changes, chunks the file, creates embeddings,
# stores vectors in Qdrant, and updates indexing metadata.

from uuid import UUID, uuid5

from qdrant_client.models import PointStruct

from app.indexing.indexer import Indexer


class RepositoryIndexer:

    def __init__(
        self,
        indexer: Indexer,
        chunker,
        embedding_service,
        vector_store,
    ):
        self.indexer = indexer
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index_file(
        self,
        repository_id: str,
        code_file,
    ):
        file_path = str(code_file.path)

        # -----------------------------------------
        # 1. Check whether file needs indexing
        # -----------------------------------------

        if not self.indexer.should_index(
            repository_id=repository_id,
            file_path=file_path,
            content=code_file.content,
        ):
            return {
                "status": "skipped",
                "path": file_path,
            }

        # -----------------------------------------
        # 2. Remove old chunks
        # -----------------------------------------

        self.vector_store.delete_file(
            repository_id=repository_id,
            file_path=file_path,
        )

        # -----------------------------------------
        # 3. Chunk
        # -----------------------------------------

        chunks = self.chunker.create_chunks(
            code_file
        )

        if not chunks:
            self.indexer.mark_indexed(
                repository_id=repository_id,
                file_path=file_path,
                content=code_file.content,
            )

            return {
                "status": "indexed",
                "path": file_path,
                "chunks": 0,
            }

        # -----------------------------------------
        # 4. Embed
        # -----------------------------------------

        texts = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_service.embed_texts(
                texts
            )
        )

        # -----------------------------------------
        # 5. Create Qdrant points
        # -----------------------------------------

        file_hash = (
            self.indexer.calculate_file_hash(
                code_file.content
            )
        )

        points = []

        for chunk_index, (
            chunk,
            embedding,
        ) in enumerate(
            zip(chunks, embeddings)
        ):
            point_id = uuid5(
                UUID(repository_id),
                f"{file_path}:{chunk_index}",
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=(
                        embedding.tolist()
                        if hasattr(embedding, "tolist")
                        else embedding
                    ),
                    payload={
                        "repository_id": repository_id,
                        "path": file_path,
                        "file_hash": file_hash,
                        "content": chunk.content,
                        "language": chunk.language,
                        "structure_type": chunk.structure_type,
                        "name": chunk.name,
                        "parent": chunk.parent,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "chunk_index": chunk_index,
                    },
                )
            )

        # -----------------------------------------
        # 6. Store vectors
        # -----------------------------------------

        self.vector_store.add_points(
            points
        )

        # -----------------------------------------
        # 7. Only now mark indexed
        # -----------------------------------------

        self.indexer.mark_indexed(
            repository_id=repository_id,
            file_path=file_path,
            content=code_file.content,
        )

        return {
            "status": "indexed",
            "path": file_path,
            "chunks": len(chunks),
        }

    def remove_deleted_files(
        self,
        repository_id: str,
        current_file_paths: set[str],
    ):
        metadata = self.indexer.metadata_store.load()

        repository = metadata.get(
            "repositories",
            {}
        ).get(
            repository_id,
            {}
        )

        indexed_files = set(
            repository.get(
                "files",
                {}
            ).keys()
        )

        deleted_files = (
            indexed_files - current_file_paths
        )

        for file_path in deleted_files:
            self.vector_store.delete_file(
                repository_id=repository_id,
                file_path=file_path,
            )

            self.indexer.metadata_store.remove_file(
                repository_id=repository_id,
                file_path=file_path,
            )

        return deleted_files