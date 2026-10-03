from unittest.mock import Mock, patch

from app.retrieval.reranker import CrossEncoderReranker


def make_chunk(content):
    chunk = Mock()
    chunk.content = content
    return chunk


@patch("app.retrieval.reranker.CrossEncoder")
def test_reranker_sorts_candidates_by_score(mock_cross_encoder):
    model = Mock()

    model.predict.return_value = [
        0.20,
        0.90,
        0.50,
    ]

    mock_cross_encoder.return_value = model

    reranker = CrossEncoderReranker()

    candidates = [
        (
            ("file1.txt", 0),
            make_chunk("First chunk"),
        ),
        (
            ("file2.txt", 0),
            make_chunk("Second chunk"),
        ),
        (
            ("file3.txt", 0),
            make_chunk("Third chunk"),
        ),
    ]

    results = reranker.rerank(
        query="authentication",
        candidates=candidates,
        limit=3,
    )

    assert results[0]["id"] == (
        "file2.txt",
        0,
    )

    assert results[0]["score"] == 0.90

    assert results[1]["id"] == (
        "file3.txt",
        0,
    )

    assert results[2]["id"] == (
        "file1.txt",
        0,
    )


@patch("app.retrieval.reranker.CrossEncoder")
def test_reranker_respects_limit(mock_cross_encoder):
    model = Mock()

    model.predict.return_value = [
        0.20,
        0.90,
        0.50,
    ]

    mock_cross_encoder.return_value = model

    reranker = CrossEncoderReranker()

    candidates = [
        (
            ("file1.txt", 0),
            make_chunk("First chunk"),
        ),
        (
            ("file2.txt", 0),
            make_chunk("Second chunk"),
        ),
        (
            ("file3.txt", 0),
            make_chunk("Third chunk"),
        ),
    ]

    results = reranker.rerank(
        query="authentication",
        candidates=candidates,
        limit=2,
    )

    assert len(results) == 2

    assert results[0]["score"] == 0.90
    assert results[1]["score"] == 0.50


@patch("app.retrieval.reranker.CrossEncoder")
def test_reranker_sends_query_document_pairs(
    mock_cross_encoder,
):
    model = Mock()

    model.predict.return_value = [
        0.80,
        0.40,
    ]

    mock_cross_encoder.return_value = model

    reranker = CrossEncoderReranker()

    candidates = [
        (
            ("auth.txt", 0),
            make_chunk("JWT authentication"),
        ),
        (
            ("payment.txt", 0),
            make_chunk("Payment retry"),
        ),
    ]

    reranker.rerank(
        query="How does authentication work?",
        candidates=candidates,
        limit=2,
    )

    model.predict.assert_called_once_with(
        [
            (
                "How does authentication work?",
                "JWT authentication",
            ),
            (
                "How does authentication work?",
                "Payment retry",
            ),
        ]
    )