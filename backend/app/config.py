from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DATABASE_URL = "sqlite:///./habit_life_rpg.db"
DEFAULT_JWT_SECRET = "replace-with-a-long-random-secret"


class Settings(BaseSettings):
    database_url: str = Field(DEFAULT_DATABASE_URL, validation_alias="DATABASE_URL")
    database_host: str | None = Field(None, validation_alias="DATABASE_HOST")
    database_name: str | None = Field(None, validation_alias="DATABASE_NAME")
    database_user: str | None = Field(None, validation_alias="DATABASE_USER")
    database_password: str | None = Field(None, validation_alias="DATABASE_PASSWORD")
    jwt_secret: str = Field(
        DEFAULT_JWT_SECRET,
        validation_alias="HLR_JWT_SECRET",
    )
    access_token_minutes: int = Field(60, validation_alias="HLR_ACCESS_TOKEN_MINUTES")
    app_timezone: str = Field("Asia/Taipei", validation_alias="HLR_APP_TIMEZONE")
    allowed_origins: str = Field(
        "http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="HLR_ALLOWED_ORIGINS",
    )
    environment: str = Field("development", validation_alias="HLR_ENVIRONMENT")
    demo_username: str = Field("book-demo", validation_alias="HLR_DEMO_USERNAME")
    demo_password: str = Field(
        "replace-with-a-demo-password",
        validation_alias="HLR_DEMO_PASSWORD",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret == DEFAULT_JWT_SECRET:
            raise ValueError("production requires a non-default JWT secret")

        azure_sql_values = (
            self.database_host,
            self.database_name,
            self.database_user,
            self.database_password,
        )
        if any(azure_sql_values) and not all(azure_sql_values):
            raise ValueError("Azure SQL settings must be provided together")
        if (
            self.environment == "production"
            and "database_url" not in self.model_fields_set
            and not all(azure_sql_values)
        ):
            raise ValueError("production requires Azure SQL settings or an explicit DATABASE_URL")
        return self

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def resolved_database_url(self) -> str:
        if "database_url" in self.model_fields_set:
            return self.database_url
        if all(
            (
                self.database_host,
                self.database_name,
                self.database_user,
                self.database_password,
            )
        ):
            connection = (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER=tcp:{self.database_host},1433;"
                f"DATABASE={self.database_name};"
                f"UID={self.database_user};"
                f"PWD={self.database_password};"
                "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
            )
            return f"mssql+pyodbc:///?odbc_connect={quote_plus(connection)}"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
