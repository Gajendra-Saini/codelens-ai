from app.retrieval.relevance import RelevanceGate


def test_relevance_gate_keeps_results_above_threshold():
    gate = RelevanceGate(
        threshold=0.5
    )

    results = [
        {
            "id": ("auth.txt", 0),
            "score": 0.9,
            "chunk": "Authentication",
        },
        {
            "id": ("payment.txt", 0),
            "score": 0.3,
            "chunk": "Payment",
        },
    ]

    decision = gate.filter(results)

    assert decision["sufficient"] is True

    assert len(decision["results"]) == 1

    assert decision["results"][0]["id"] == (
        "auth.txt",
        0,
    )


def test_relevance_gate_returns_insufficient_when_no_result_passes():
    gate = RelevanceGate(
        threshold=0.5
    )

    results = [
        {
            "id": ("auth.txt", 0),
            "score": 0.3,
            "chunk": "Authentication",
        },
        {
            "id": ("payment.txt", 0),
            "score": 0.2,
            "chunk": "Payment",
        },
    ]

    decision = gate.filter(results)

    assert decision["sufficient"] is False

    assert decision["results"] == []


def test_relevance_gate_keeps_result_at_exact_threshold():
    gate = RelevanceGate(
        threshold=0.5
    )

    results = [
        {
            "id": ("auth.txt", 0),
            "score": 0.5,
            "chunk": "Authentication",
        },
    ]

    decision = gate.filter(results)

    assert decision["sufficient"] is True

    assert len(decision["results"]) == 1