from google import genai
from google.genai import errors

from app.core.config import settings
from app.core.exceptions import (
    GenerationUnavailableError,
)


class LLMService:

    def __init__(
        self,
        model: str = "gemini-3.8-flash",
        client=None,
    ):

        self.client = (
            client
            or genai.Client(
                api_key=settings.gemini_api_key
            )
        )

        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ):

        try:

            response = (
                self.client.models.generate_content(
                    model=self.model,
                    contents=user_prompt,
                    config={
                        "system_instruction":
                            system_prompt
                    },
                )
            )

            return response.text

        except errors.ServerError as exc:

            raise GenerationUnavailableError(
                "The generation service is "
                "temporarily unavailable."
            ) from exc