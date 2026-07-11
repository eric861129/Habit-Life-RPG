from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field("sqlite:///./habit_life_rpg.db", validation_alias="DATABASE_URL")
    jwt_secret: str = Field(
        "replace-with-a-long-random-secret",
        validation_alias="HLR_JWT_SECRET",
    )
    access_token_minutes: int = Field(60, validation_alias="HLR_ACCESS_TOKEN_MINUTES")
    app_timezone: str = Field("Asia/Taipei", validation_alias="HLR_APP_TIMEZONE")
    allowed_origins: str = Field(
        "http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="HLR_ALLOWED_ORIGINS",
    )
    environment: str = Field("development", validation_alias="HLR_ENVIRONMENT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
