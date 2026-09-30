from app.indexing.indexer import Indexer
from app.indexing.metadata import IndexMetadataStore


def create_indexer(tmp_path):

    metadata_store = IndexMetadataStore(
        metadata_path=tmp_path / "index_metadata.json"
    )

    return Indexer(
        metadata_store=metadata_store
    )


def test_calculate_file_hash_is_deterministic(tmp_path):

    indexer = create_indexer(tmp_path)

    content = "authentication logic"

    hash1 = indexer.calculate_file_hash(content)
    hash2 = indexer.calculate_file_hash(content)

    assert hash1 == hash2


def test_different_content_produces_different_hash(tmp_path):

    indexer = create_indexer(tmp_path)

    hash1 = indexer.calculate_file_hash(
        "authentication logic"
    )

    hash2 = indexer.calculate_file_hash(
        "payment logic"
    )

    assert hash1 != hash2


def test_new_file_should_be_indexed(tmp_path):

    indexer = create_indexer(tmp_path)

    should_index = indexer.should_index(
        repository_id="repo-1",
        file_path="auth.txt",
        content="authentication logic",
    )

    assert should_index is True


def test_unchanged_file_should_not_be_indexed(tmp_path):

    indexer = create_indexer(tmp_path)

    content = "authentication logic"

    indexer.mark_indexed(
        repository_id="repo-1",
        file_path="auth.txt",
        content=content,
    )

    should_index = indexer.should_index(
        repository_id="repo-1",
        file_path="auth.txt",
        content=content,
    )

    assert should_index is False


def test_changed_file_should_be_indexed(tmp_path):

    indexer = create_indexer(tmp_path)

    indexer.mark_indexed(
        repository_id="repo-1",
        file_path="auth.txt",
        content="old authentication logic",
    )

    should_index = indexer.should_index(
        repository_id="repo-1",
        file_path="auth.txt",
        content="new authentication logic",
    )

    assert should_index is True


def test_mark_indexed_stores_metadata(tmp_path):

    indexer = create_indexer(tmp_path)

    indexer.mark_indexed(
        repository_id="repo-1",
        file_path="auth.txt",
        content="authentication logic",
    )

    metadata = indexer.metadata_store.load()

    assert "repo-1" in metadata["repositories"]

    assert "auth.txt" in (
        metadata["repositories"]["repo-1"]["files"]
    )

    file_metadata = (
        metadata["repositories"]
        ["repo-1"]
        ["files"]
        ["auth.txt"]
    )

    assert file_metadata["hash"] == (
        indexer.calculate_file_hash(
            "authentication logic"
        )
    )

    assert file_metadata["indexed"] is True


def test_different_repositories_have_separate_metadata(tmp_path):

    indexer = create_indexer(tmp_path)

    indexer.mark_indexed(
        repository_id="repo-1",
        file_path="auth.txt",
        content="repo one authentication",
    )

    indexer.mark_indexed(
        repository_id="repo-2",
        file_path="auth.txt",
        content="repo two authentication",
    )

    metadata = indexer.metadata_store.load()

    assert "auth.txt" in (
        metadata["repositories"]["repo-1"]["files"]
    )

    assert "auth.txt" in (
        metadata["repositories"]["repo-2"]["files"]
    )

    assert (
        metadata["repositories"]["repo-1"]["files"]["auth.txt"]["hash"]
        !=
        metadata["repositories"]["repo-2"]["files"]["auth.txt"]["hash"]
    )


def test_remove_file_from_metadata(tmp_path):

    indexer = create_indexer(tmp_path)

    indexer.mark_indexed(
        repository_id="repo-1",
        file_path="auth.txt",
        content="authentication logic",
    )

    indexer.metadata_store.remove_file(
        repository_id="repo-1",
        file_path="auth.txt",
    )

    metadata = indexer.metadata_store.load()

    assert "auth.txt" not in (
        metadata["repositories"]["repo-1"]["files"]
    )


def test_remove_nonexistent_file_does_not_fail(tmp_path):

    indexer = create_indexer(tmp_path)

    indexer.metadata_store.remove_file(
        repository_id="repo-1",
        file_path="missing.txt",
    )