class FakeRetrievalPipeline:

    def run(self, query):
        return {
            "sufficient": True,
            "context": "File: auth.txt\nvalidate_token() handles authentication.",
            "results": [
                {
                    "id": ("auth.txt", 0),
                    "score": 0.95,
                    "chunk": "validate_token() handles authentication.",
                }
            ],
        }


class FakePromptBuilder:

    def build(self, query, context):
        return {
            "system": "You are CodeLens AI.",
            "user": f"{context}\nQuestion: {query}",
        }


class FakeLLMService:

    def generate(self, system_prompt, user_prompt):
        return "Authentication is handled by validate_token()."


def test_query_service_generates_answer():

    from app.generation.query_service import QueryService

    service = QueryService(
        retrieval_pipeline=FakeRetrievalPipeline(),
        prompt_builder=FakePromptBuilder(),
        llm_service=FakeLLMService(),
    )

    result = service.answer(
        "Where is authentication handled?"
    )

    assert result["sufficient"] is True

    assert (
        result["answer"]
        == "Authentication is handled by validate_token()."
    )

    assert len(result["results"]) == 1

class EmptyRetrievalPipeline:

    def run(self, query):
        return {
            "sufficient": False,
            "context": None,
            "results": [],
        }


class FailingLLMService:

    def generate(self, system_prompt, user_prompt):
        raise AssertionError(
            "LLM should not be called when evidence is insufficient"
        )


def test_query_service_stops_when_evidence_is_insufficient():

    from app.generation.query_service import QueryService

    service = QueryService(
        retrieval_pipeline=EmptyRetrievalPipeline(),
        prompt_builder=FakePromptBuilder(),
        llm_service=FailingLLMService(),
    )

    result = service.answer(
        "Where is authentication handled?"
    )

    assert result["sufficient"] is False

    assert (
        result["answer"]
        == "Sufficient evidence was not found in the repository."
    )

    assert result["results"] == []