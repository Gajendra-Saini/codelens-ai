class ReciprocalRankFusion:

    def __init__(
        self,
        k: int = 60,
    ):
        self.k = k

    def fuse(
        self,
        ranked_lists: list[list[int]],
    ):

        scores = {}

        for ranked_list in ranked_lists:

            for rank, document_id in enumerate(
                ranked_list,
                start=1,
            ):

                score = 1 / (
                    self.k + rank
                )

                scores[document_id] = (
                    scores.get(document_id, 0)
                    + score
                )

        return sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )