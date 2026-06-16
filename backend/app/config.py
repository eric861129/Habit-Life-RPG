from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field("sqlite:///./habit_life_rpg.db", validation_alias="DATABASE_URL")
    dev_auth_token: str = Field("local-dev-token", validation_alias="HLR_DEV_AUTH_TOKEN")
    demo_user_id: int = Field(1, validation_alias="HLR_DEMO_USER_ID")
    app_timezone: str = Field("Asia/Taipei", validation_alias="HLR_APP_TIMEZONE")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
