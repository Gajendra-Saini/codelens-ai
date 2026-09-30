import uuid

import pytest
from qdrant_client.models import PointStruct

from app.vectorstore.qdrant import QdrantVectorStore


COLLECTION_NAME = f"test_codelens_{uuid.uuid4().hex}"


@pytest.fixture
def vector_store():

    store = QdrantVectorStore(
        collection_name=COLLECTION_NAME,
        vector_size=3,
    )

    yield store

    store.client.delete_collection(
        collection_name=COLLECTION_NAME
    )


def test_collection_is_created(vector_store):

    assert vector_store.client.collection_exists(
        collection_name=COLLECTION_NAME
    )


def test_add_points_and_search(vector_store):

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[1.0, 0.0, 0.0],
            payload={
                "repository_id": "repo-1",
                "path": "auth.txt",
                "content": "authentication logic",
            },
        ),
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[0.0, 1.0, 0.0],
            payload={
                "repository_id": "repo-1",
                "path": "payment.txt",
                "content": "payment logic",
            },
        ),
    ]

    vector_store.add_points(points)

    results = vector_store.search(
        query_vector=points[0].vector,
        limit=1,
    )

    assert len(results) == 1
    assert results[0].payload["path"] == "auth.txt"


def test_search_respects_limit(vector_store):

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[1.0, 0.0, 0.0],
            payload={"path": "auth.txt"},
        ),
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[0.9, 0.1, 0.0],
            payload={"path": "payment.txt"},
        ),
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[0.8, 0.2, 0.0],
            payload={"path": "database.txt"},
        ),
    ]

    vector_store.add_points(points)

    results = vector_store.search(
        query_vector=points[0].vector,
        limit=2,
    )

    assert len(results) == 2


def test_delete_file_removes_matching_points(vector_store):

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[1.0, 0.0, 0.0],
            payload={
                "repository_id": "repo-1",
                "path": "auth.txt",
            },
        ),
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[0.0, 1.0, 0.0],
            payload={
                "repository_id": "repo-1",
                "path": "payment.txt",
            },
        ),
        PointStruct(
            id=str(uuid.uuid4()),
            vector=[0.0, 0.0, 1.0],
            payload={
                "repository_id": "repo-2",
                "path": "auth.txt",
            },
        ),
    ]

    vector_store.add_points(points)

    vector_store.delete_file(
        repository_id="repo-1",
        file_path="auth.txt",
    )

    results = vector_store.search(
        query_vector=[1.0, 0.0, 0.0],
        limit=10,
    )

    remaining = [
        result.payload
        for result in results
    ]

    assert not any(
        payload["repository_id"] == "repo-1"
        and payload["path"] == "auth.txt"
        for payload in remaining
    )

    assert any(
        payload["repository_id"] == "repo-1"
        and payload["path"] == "payment.txt"
        for payload in remaining
    )

    assert any(
        payload["repository_id"] == "repo-2"
        and payload["path"] == "auth.txt"
        for payload in remaining
    )