from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    APP_ENV: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def reload(self) -> bool:
        return self.DEBUG or self.APP_ENV != "prod"

settings = Settings()
