class FakeResponse:

    text = "This is a generated answer."


class FakeModels:

    def __init__(self):
        self.last_call = None

    def generate_content(
        self,
        model,
        contents,
        config,
    ):
        self.last_call = {
            "model": model,
            "contents": contents,
            "config": config,
        }

        return FakeResponse()


class FakeClient:

    def __init__(self):
        self.models = FakeModels()


def test_llm_service_generates_answer():

    from app.generation.llm import LLMService

    client = FakeClient()

    service = LLMService(
        model="test-model",
        client=client,
    )

    result = service.generate(
        system_prompt="You are a code assistant.",
        user_prompt="Explain this code.",
    )

    assert result == "This is a generated answer."

    assert client.models.last_call["model"] == "test-model"

    assert (
        client.models.last_call["contents"]
        == "Explain this code."
    )

    assert (
        client.models.last_call["config"]["system_instruction"]
        == "You are a code assistant."
    )