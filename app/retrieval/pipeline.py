class RetrievalPipeline:

    def __init__(
        self,
        retriever,
        relevance_gate,
        context_builder,
    ):
        self.retriever = retriever
        self.relevance_gate = relevance_gate
        self.context_builder = context_builder

    def run(
        self,
        query: str,
        limit: int = 5,
    ):

        # 1. Retrieve candidates
        results = self.retriever.retrieve(
            query=query,
            limit=limit,
        )

        # 2. Check evidence
        decision = self.relevance_gate.filter(
            results
        )

        # 3. Stop if evidence is insufficient
        if not decision["sufficient"]:
            return {
                "sufficient": False,
                "context": None,
                "results": [],
            }

        # 4. Build context
        context = self.context_builder.build(
            decision["results"]
        )

        return {
            "sufficient": True,
            "context": context,
            "results": decision["results"],
        }