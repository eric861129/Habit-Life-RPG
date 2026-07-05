from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.database import SessionLocal, init_db
from backend.app.routers import habits, user
from backend.app.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)
    yield


def create_app(*, enable_startup_seed: bool = True) -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Habit Life RPG API",
        version="0.8.0",
        description="Document-driven Habit Life RPG API.",
        lifespan=lifespan if enable_startup_seed else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(user.router)
    app.include_router(habits.router)
    return app


app = create_app()
