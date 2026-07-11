import pytest
from pydantic import ValidationError

from backend.app.config import Settings


def test_production_rejects_the_default_jwt_secret():
    with pytest.raises(ValidationError, match="production requires a non-default JWT secret"):
        Settings(HLR_ENVIRONMENT="production")


def test_azure_sql_fields_build_an_encoded_sqlalchemy_url():
    settings = Settings(
        HLR_ENVIRONMENT="production",
        HLR_JWT_SECRET="a-real-deployment-secret-that-is-long",
        DATABASE_HOST="hlr-example.database.windows.net",
        DATABASE_NAME="habit-life-rpg",
        DATABASE_USER="hlradmin",
        DATABASE_PASSWORD="p@ss word/with?symbols",
    )

    url = settings.resolved_database_url

    assert url.startswith("mssql+pyodbc:///?odbc_connect=")
    assert "PWD%3Dp%40ss+word%2Fwith%3Fsymbols%3B" in url
    assert "SERVER%3Dtcp%3Ahlr-example.database.windows.net%2C1433%3B" in url
    assert "TrustServerCertificate%3Dno" in url


def test_partial_azure_sql_configuration_is_rejected():
    with pytest.raises(ValidationError, match="Azure SQL settings must be provided together"):
        Settings(DATABASE_HOST="hlr-example.database.windows.net")


def test_explicit_database_url_remains_available_for_local_development():
    settings = Settings(DATABASE_URL="sqlite:///./local.db")

    assert settings.resolved_database_url == "sqlite:///./local.db"
