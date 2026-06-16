from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.database import SessionLocal, init_db
from backend.app.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Habit Life RPG API",
        version="0.5.0",
        description="Chapter 5 local FastAPI backend for Habit Life RPG.",
        lifespan=lifespan,
    )
    return app


app = create_app()
