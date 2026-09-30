from pathlib import Path
from unittest.mock import Mock
from uuid import uuid4

from app.indexing.repository_indexer import RepositoryIndexer
from app.repositories.models import CodeChunk, CodeFile


REPOSITORY_ID = str(uuid4())


def create_code_file(
    content="authentication logic",
    path="auth.txt",
):

    return CodeFile(
        repository_id=uuid4(),
        path=Path(path),
        language="text",
        content=content,
        size=len(content.encode("utf-8")),
    )


def create_chunk(
    content="authentication logic",
    path="auth.txt",
):

    return CodeChunk(
        content=content,
        path=Path(path),
        language="text",
        structure_type="text",
        name=Path(path).name,
        parent=None,
        start_line=0,
        end_line=0,
    )


def create_repository_indexer():

    indexer = Mock()
    chunker = Mock()
    embedding_service = Mock()
    vector_store = Mock()

    indexer.metadata_store = Mock()

    repository_indexer = RepositoryIndexer(
        indexer=indexer,
        chunker=chunker,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    return (
        repository_indexer,
        indexer,
        chunker,
        embedding_service,
        vector_store,
    )


def test_new_file_is_indexed():

    (
        repository_indexer,
        indexer,
        chunker,
        embedding_service,
        vector_store,
    ) = create_repository_indexer()

    code_file = create_code_file()

    indexer.should_index.return_value = True

    chunks = [
        create_chunk("authentication logic"),
        create_chunk("authorization logic"),
    ]

    chunker.create_chunks.return_value = chunks

    embedding_service.embed_texts.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    result = repository_indexer.index_file(
        repository_id=REPOSITORY_ID,
        code_file=code_file,
    )

    assert result["status"] == "indexed"
    assert result["path"] == "auth.txt"
    assert result["chunks"] == 2

    indexer.should_index.assert_called_once()

    vector_store.delete_file.assert_called_once_with(
        repository_id=REPOSITORY_ID,
        file_path="auth.txt",
    )

    chunker.create_chunks.assert_called_once_with(
        code_file
    )

    embedding_service.embed_texts.assert_called_once_with(
        [
            "authentication logic",
            "authorization logic",
        ]
    )

    vector_store.add_points.assert_called_once()

    indexer.mark_indexed.assert_called_once_with(
        repository_id=REPOSITORY_ID,
        file_path="auth.txt",
        content=code_file.content,
    )


def test_unchanged_file_is_skipped():

    (
        repository_indexer,
        indexer,
        chunker,
        embedding_service,
        vector_store,
    ) = create_repository_indexer()

    code_file = create_code_file()

    indexer.should_index.return_value = False

    result = repository_indexer.index_file(
        repository_id=REPOSITORY_ID,
        code_file=code_file,
    )

    assert result == {
        "status": "skipped",
        "path": "auth.txt",
    }

    chunker.create_chunks.assert_not_called()
    embedding_service.embed_texts.assert_not_called()
    vector_store.delete_file.assert_not_called()
    vector_store.add_points.assert_not_called()
    indexer.mark_indexed.assert_not_called()


def test_changed_file_deletes_old_vectors_before_indexing():

    (
        repository_indexer,
        indexer,
        chunker,
        embedding_service,
        vector_store,
    ) = create_repository_indexer()

    code_file = create_code_file(
        content="updated authentication logic"
    )

    indexer.should_index.return_value = True

    chunker.create_chunks.return_value = [
        create_chunk(
            "updated authentication logic"
        )
    ]

    embedding_service.embed_texts.return_value = [
        [0.1, 0.2, 0.3]
    ]

    repository_indexer.index_file(
        repository_id=REPOSITORY_ID,
        code_file=code_file,
    )

    vector_store.delete_file.assert_called_once_with(
        repository_id=REPOSITORY_ID,
        file_path="auth.txt",
    )

    vector_store.add_points.assert_called_once()


def test_point_payload_contains_chunk_information():

    (
        repository_indexer,
        indexer,
        chunker,
        embedding_service,
        vector_store,
    ) = create_repository_indexer()

    code_file = create_code_file()

    indexer.should_index.return_value = True

    chunker.create_chunks.return_value = [
        create_chunk(
            "authentication logic"
        )
    ]

    embedding_service.embed_texts.return_value = [
        [0.1, 0.2, 0.3]
    ]

    repository_indexer.index_file(
        repository_id=REPOSITORY_ID,
        code_file=code_file,
    )

    points = vector_store.add_points.call_args.args[0]

    assert len(points) == 1

    payload = points[0].payload

    assert payload["repository_id"] == REPOSITORY_ID
    assert payload["path"] == "auth.txt"
    assert payload["content"] == "authentication logic"
    assert payload["language"] == "text"
    assert payload["structure_type"] == "text"
    assert payload["name"] == "auth.txt"
    assert payload["chunk_index"] == 0


def test_multiple_chunks_get_unique_point_ids():

    (
        repository_indexer,
        indexer,
        chunker,
        embedding_service,
        vector_store,
    ) = create_repository_indexer()

    code_file = create_code_file()

    indexer.should_index.return_value = True

    chunker.create_chunks.return_value = [
        create_chunk("first chunk"),
        create_chunk("second chunk"),
        create_chunk("third chunk"),
    ]

    embedding_service.embed_texts.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.7, 0.8, 0.9],
    ]

    repository_indexer.index_file(
        repository_id=REPOSITORY_ID,
        code_file=code_file,
    )

    points = vector_store.add_points.call_args.args[0]

    point_ids = [
        point.id
        for point in points
    ]

    assert len(point_ids) == 3
    assert len(set(point_ids)) == 3


def test_empty_chunks_do_not_create_vectors():

    (
        repository_indexer,
        indexer,
        chunker,
        embedding_service,
        vector_store,
    ) = create_repository_indexer()

    code_file = create_code_file(
        content=""
    )

    indexer.should_index.return_value = True

    chunker.create_chunks.return_value = []

    embedding_service.embed_texts.return_value = []

    result = repository_indexer.index_file(
        repository_id=REPOSITORY_ID,
        code_file=code_file,
    )

    assert result["status"] == "indexed"
    assert result["chunks"] == 0

    
    embedding_service.embed_texts.assert_not_called()
    indexer.mark_indexed.assert_called_once()


def test_deleted_files_are_removed():

    (
        repository_indexer,
        indexer,
        chunker,
        embedding_service,
        vector_store,
    ) = create_repository_indexer()

    indexer.metadata_store.load.return_value = {
        "repositories": {
            REPOSITORY_ID: {
                "files": {
                    "auth.txt": {
                        "hash": "abc",
                        "indexed": True,
                    },
                    "payment.txt": {
                        "hash": "def",
                        "indexed": True,
                    },
                    "old.txt": {
                        "hash": "xyz",
                        "indexed": True,
                    },
                }
            }
        }
    }

    current_file_paths = {
        "auth.txt",
        "payment.txt",
    }

    deleted_files = repository_indexer.remove_deleted_files(
        repository_id=REPOSITORY_ID,
        current_file_paths=current_file_paths,
    )

    assert deleted_files == {"old.txt"}

    vector_store.delete_file.assert_called_once_with(
        repository_id=REPOSITORY_ID,
        file_path="old.txt",
    )

    indexer.metadata_store.remove_file.assert_called_once_with(
        repository_id=REPOSITORY_ID,
        file_path="old.txt",
    )