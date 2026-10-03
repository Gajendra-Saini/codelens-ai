# Orchestrates retrieval, prompt building, and LLM generation.

class QueryService:

    def __init__(
        self,
        retrieval_pipeline,
        prompt_builder,
        llm_service,
    ):
        self.retrieval_pipeline = retrieval_pipeline
        self.prompt_builder = prompt_builder
        self.llm_service = llm_service

    def answer(self, query: str):

        retrieval_result = self.retrieval_pipeline.run(
            query=query,
        )

        if not retrieval_result["sufficient"]:
            return {
                "answer": (
                    "Sufficient evidence was not found "
                    "in the repository."
                ),
                "sufficient": False,
                "results": [],
            }

        prompts = self.prompt_builder.build(
            query=query,
            context=retrieval_result["context"],
        )

        answer = self.llm_service.generate(
            system_prompt=prompts["system"],
            user_prompt=prompts["user"],
        )

        return {
            "answer": answer,
            "sufficient": True,
            "results": retrieval_result["results"],
        }