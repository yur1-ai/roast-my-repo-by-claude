from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM providers
    google_api_key: str = ""
    groq_api_key: str = ""
    llm_provider: str = "gemini"

    # GitHub
    github_token: str = ""

    # App
    database_url: str = "sqlite+aiosqlite:///./roasts.db"
    frontend_url: str = "http://localhost:5173"
    environment: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
