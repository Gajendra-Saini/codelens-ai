from unittest.mock import Mock

from app.retrieval.retriever import Retriever


def make_chunk(path, content):
    chunk = Mock()
    chunk.path = path
    chunk.content = content
    return chunk


def test_bm25_uses_canonical_chunk_ids():
    chunks = [
        make_chunk(
            "auth.txt",
            "JWT authentication",
        ),
        make_chunk(
            "auth.txt",
            "Token validation",
        ),
        make_chunk(
            "payment.txt",
            "Payment retry",
        ),
    ]

    embedding_service = Mock()
    vector_store = Mock()
    rrf = Mock()
    reranker = Mock()

    embedding_service.embed_text.return_value = [
        0.1,
        0.2,
    ]

    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        chunks=chunks,
        rrf=rrf,
        reranker=reranker,
    )

    results = retriever.bm25_retrieve(
        "authentication",
        limit=3,
    )

    returned_ids = [
        result["id"]
        for result in results
    ]

    assert all(
        isinstance(chunk_id, tuple)
        for chunk_id in returned_ids
    )

    assert all(
        len(chunk_id) == 2
        for chunk_id in returned_ids
    )


def test_dense_results_can_be_converted_to_canonical_ids():
    chunks = [
        make_chunk(
            "auth.txt",
            "JWT authentication",
        ),
        make_chunk(
            "auth.txt",
            "Token validation",
        ),
    ]

    embedding_service = Mock()
    vector_store = Mock()
    rrf = Mock()
    reranker = Mock()

    embedding_service.embed_text.return_value = [
        0.1,
        0.2,
    ]

    point = Mock()

    point.id = "qdrant-uuid-123"

    point.payload = {
        "path": "auth.txt",
        "chunk_index": 1,
        "content": "Token validation",
        "language": "text",
        "structure_type": "text",
        "name": "auth.txt",
        "parent": None,
        "start_line": 0,
        "end_line": 0,
    }

    vector_store.search.return_value = [
        point
    ]

    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        chunks=chunks,
        rrf=rrf,
        reranker=reranker,
    )

    dense_results = retriever.dense_retrieve(
        "authentication",
        limit=5,
    )

    dense_ids = [
        (
            result.payload["path"],
            result.payload["chunk_index"],
        )
        for result in dense_results
    ]

    assert dense_ids == [
        ("auth.txt", 1)
    ]
def test_full_retrieval_pipeline_uses_canonical_ids():
    chunks = [
        make_chunk(
            "auth.txt",
            "JWT authentication",
        ),
        make_chunk(
            "auth.txt",
            "Token validation",
        ),
        make_chunk(
            "payment.txt",
            "Payment retry",
        ),
    ]

    embedding_service = Mock()
    vector_store = Mock()
    rrf = Mock()
    reranker = Mock()

    embedding_service.embed_text.return_value = [
        0.1,
        0.2,
    ]

    dense_point = Mock()

    dense_point.id = "qdrant-uuid-123"

    dense_point.payload = {
        "path": "auth.txt",
        "chunk_index": 1,
    }

    vector_store.search.return_value = [
        dense_point
    ]

    rrf.fuse.return_value = [
        (
            ("auth.txt", 1),
            0.05,
        )
    ]

    reranker.rerank.return_value = [
        {
            "id": ("auth.txt", 1),
            "score": 0.95,
            "chunk": chunks[1],
        }
    ]

    retriever = Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        chunks=chunks,
        rrf=rrf,
        reranker=reranker,
    )

    results = retriever.retrieve(
        query="How does authentication work?",
        limit=5,
        candidate_limit=20,
    )

    rrf.fuse.assert_called_once_with(
        [
            [("auth.txt", 1)],
            [
                result["id"]
                for result in retriever.bm25_retrieve(
                    "How does authentication work?",
                    limit=20,
                )
            ],
        ]
    )

    reranker.rerank.assert_called_once()

    call_args = reranker.rerank.call_args

    candidates = call_args.kwargs["candidates"]

    assert candidates == [
        (
            ("auth.txt", 1),
            chunks[1],
        )
    ]

    assert results[0]["id"] == (
        "auth.txt",
        1,
    )