"""Bot sozlamalari (.env dan)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str = ""
    # Bot backendga ichki tarmoq orqali murojaat qiladi.
    api_url: str = "http://localhost:8000"
    # Botning backenddagi maxsus kaliti (1-bosqichdan ishlatiladi).
    bot_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
