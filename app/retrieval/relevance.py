class RelevanceGate:

    def __init__(self, threshold: float):
        self.threshold = threshold

    def filter(self, results):

        filtered_results = [
            result
            for result in results
            if result["score"] >= self.threshold
        ]

        return {
            "sufficient": len(filtered_results) > 0,
            "results": filtered_results,
        }