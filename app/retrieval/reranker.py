from sentence_transformers import CrossEncoder


class CrossEncoderReranker:

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.model = CrossEncoder(
            model_name
        )

    def rerank(
        self,
        query: str,
        candidates,
        limit: int = 5,
    ):

        pairs = [
            (
                query,
                chunk.content,
            )
            for chunk_id, chunk in candidates
        ]

        scores = self.model.predict(
            pairs
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        return [
            {
                "id": candidates[index][0],
                "score": float(scores[index]),
                "chunk": candidates[index][1],
            }
            for index in ranked_indices[:limit]
        ]