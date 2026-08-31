FROM python:3.12-slim-bookworm

ARG GIT_SHA=unknown

LABEL org.opencontainers.image.source="https://github.com/eric861129/Habit-Life-RPG"
LABEL org.opencontainers.image.revision="${GIT_SHA}"
LABEL org.opencontainers.image.description="Habit Life RPG book demo API"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl gnupg \
    && curl --fail --silent --show-error --location \
        https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor --output /usr/share/keyrings/microsoft-prod.gpg \
    && curl --fail --silent --show-error --location \
        https://packages.microsoft.com/config/debian/12/prod.list \
        --output /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install --yes --no-install-recommends \
        libgssapi-krb5-2 \
        msodbcsql18 \
        unixodbc \
    && apt-get purge --yes --auto-remove curl gnupg \
    && apt-get clean \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

COPY --chown=10001:10001 pyproject.toml alembic.ini ./
COPY --chown=10001:10001 backend ./backend
COPY --chown=10001:10001 migrations ./migrations

RUN python -m pip install --no-cache-dir ".[azure]"

USER 10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2)"]

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
