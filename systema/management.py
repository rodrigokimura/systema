from pathlib import Path

from pydantic import DirectoryPath, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__name__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="systema_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    secret_key: str = ""
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    base_path: DirectoryPath = Field(default=str(BASE_DIR))
    db_address: str = Field(default=f"sqlite:///{BASE_DIR}/database.db")


settings = Settings()
