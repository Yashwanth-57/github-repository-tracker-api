from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    HTTP_TIMEOUT: int = 10
    GITHUB_API_BASE_URL: str = "https://api.github.com"
    GITHUB_TOKEN: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env"
    )


settings = Settings()