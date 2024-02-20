import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="systema_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    secret_key: str = ""
    algorithm: str = ""
    access_token_expire_minutes: int = 30


settings = Settings()


def flush():
    os.remove("database.db")
