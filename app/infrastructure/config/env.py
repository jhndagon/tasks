from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    port: int = Field(default=8000, alias="PORT")
    turso_database_url: str = Field(alias="TURSO_DATABASE_URL")
    turso_auth_token: str | None = Field(default=None, alias="TURSO_AUTH_TOKEN")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
