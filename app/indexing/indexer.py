# This file tracks which files have been indexed
# and detects whether a file has changed since the last index.


from app.indexing.metadata import IndexMetadataStore


class Indexer:

    def __init__(
        self,
        metadata_store: IndexMetadataStore | None = None,
    ):

        self.metadata_store = (
            metadata_store
            or IndexMetadataStore()
        )

    def calculate_file_hash(
        self,
        content: str,
    ) -> str:

        import hashlib

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    def should_index(
        self,
        repository_id: str,
        file_path: str,
        content: str,
    ) -> bool:

        metadata = self.metadata_store.load()

        repository = metadata.get(
            "repositories",
            {}
        ).get(
            repository_id,
            {}
        )

        file_metadata = repository.get(
            "files",
            {}
        ).get(
            file_path
        )

        if file_metadata is None:
            return True

        current_hash = self.calculate_file_hash(
            content
        )

        stored_hash = file_metadata.get(
            "hash"
        )

        return current_hash != stored_hash

    def mark_indexed(
        self,
        repository_id: str,
        file_path: str,
        content: str,
    ):

        metadata = self.metadata_store.load()

        repositories = metadata.setdefault(
            "repositories",
            {}
        )

        repository = repositories.setdefault(
            repository_id,
            {}
        )

        files = repository.setdefault(
            "files",
            {}
        )

        files[file_path] = {
            "hash": self.calculate_file_hash(
                content
            ),
            "indexed": True,
        }

        self.metadata_store.save(
            metadata
        )