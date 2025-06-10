from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    SUPABASE_URL: str = os.getenv("SUPABASE_URL") or ""
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY") or ""
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY") or ""
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2") or ""
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY") or ""
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY") or ""
    IS_DEVELOPMENT: bool = os.getenv("IS_DEVELOPMENT", "false").lower() == "true"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
