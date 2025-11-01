from pydantic_settings import BaseSettings, SettingsConfigDict

class _Settings(BaseSettings):
    host: str
    port: int
    app_env: str
    debug: bool
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def reload(self) -> bool:
        return self.DEBUG or self.APP_ENV != "prod"

settings = _Settings()
