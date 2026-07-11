import os

from backend.app.config import Settings


AZURE_SQL_ENVIRONMENT_KEYS = (
    "DATABASE_HOST",
    "DATABASE_NAME",
    "DATABASE_USER",
    "DATABASE_PASSWORD",
)


def resolve_migration_database_url(configured_url: str | None) -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url
    if any(os.getenv(key) for key in AZURE_SQL_ENVIRONMENT_KEYS):
        return Settings().resolved_database_url
    return configured_url or Settings().resolved_database_url
