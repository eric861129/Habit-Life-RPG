from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.routers import auth, habits, health, user


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Habit Life RPG API",
        version="0.6.0",
        description="Complete book MVP API for Habit Life RPG.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.get("/", include_in_schema=False)
    def service_root() -> dict[str, str]:
        return {
            "name": "Habit Life RPG API",
            "docs": "/docs",
            "health": "/health/ready",
        }

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(user.router)
    app.include_router(habits.router)
    return app


app = create_app()
