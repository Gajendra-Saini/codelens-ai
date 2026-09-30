# This file manages the index metadata stored in index_metadata.json.
# It reads, writes, and removes file metadata used for incremental indexing.


import json

from pathlib import Path


class IndexMetadataStore:

    def __init__(
        self,
        metadata_path: str = "storage/index_metadata.json",
    ):
        self.metadata_path = Path(
            metadata_path
        )

        self.metadata_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def load(self) -> dict:
        if not self.metadata_path.exists():
            return {}

        return json.loads(
            self.metadata_path.read_text(
                encoding="utf-8"
            )
        )

    def save(
        self,
        metadata: dict,
    ):
        self.metadata_path.write_text(
            json.dumps(
                metadata,
                indent=2,
            ),
            encoding="utf-8",
        )

    def remove_file(
        self,
        repository_id: str,
        file_path: str,
    ):
        metadata = self.load()

        repository = metadata.get(
            "repositories",
            {}
        ).get(
            repository_id
        )

        if repository is None:
            return

        files = repository.get(
            "files",
            {}
        )

        files.pop(
            file_path,
            None
        )

        self.save(metadata)