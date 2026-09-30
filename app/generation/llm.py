from google import genai

from app.core.config import settings


class LLMService:

    def __init__(
        self,
        model: str = "gemini-3.7-flash",
    ):

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ):

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config={
                "system_instruction": system_prompt,
            },
        )

        return response.text