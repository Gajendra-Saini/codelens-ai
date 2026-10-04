# This file manages the application configuration.
# It loads settings such as the app name, environment,
# and Gemini API key from the .env file.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "CodeLens AI"

    environment: str = "development"

    gemini_api_key: str

    qdrant_url: str = "http://localhost:6333"

    qdrant_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()