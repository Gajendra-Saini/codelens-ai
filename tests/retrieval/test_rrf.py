from app.retrieval.rrf import ReciprocalRankFusion


def test_rrf_combines_rankings():
    rrf = ReciprocalRankFusion(k=60)

    results = rrf.fuse(
        [
            ["A", "B", "C"],
            ["B", "A", "D"],
        ]
    )

    scores = dict(results)

    assert scores["A"] == scores["B"]

    assert scores["A"] > scores["C"]
    assert scores["A"] > scores["D"]


def test_rrf_rewards_documents_present_in_multiple_lists():
    rrf = ReciprocalRankFusion(k=60)

    results = rrf.fuse(
        [
            ["A", "B", "C"],
            ["A", "D", "E"],
        ]
    )

    scores = dict(results)

    assert scores["A"] > scores["B"]
    assert scores["A"] > scores["D"]
    assert scores["A"] > scores["C"]


def test_rrf_returns_results_in_descending_score_order():
    rrf = ReciprocalRankFusion(k=60)

    results = rrf.fuse(
        [
            ["A", "B"],
            ["A", "C"],
        ]
    )

    scores = [score for _, score in results]

    assert scores == sorted(
        scores,
        reverse=True,
    )