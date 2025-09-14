from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_PROVIDER: str = "openai"
    MODEL_NAME: str = "gpt-4o-mini"
    MODEL_NAME_BIG: str = "gpt-4o"
    OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
