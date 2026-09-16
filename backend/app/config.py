from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ThreadPilot"
    version: str = "5.0.0"
    environment: str = "production"
    database_url: str = "postgresql+psycopg://threadpilot:threadpilot@db:5432/threadpilot"
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str = "gpt-4.1-mini"
    cors_origins: str = "*"
    seed_demo: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

def database_url():
    url=settings.database_url
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"): ]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"): ]
    return url

