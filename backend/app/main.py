from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import SessionLocal, init_db
from backend.app.routers import habits, user
from backend.app.seed import seed_demo_data

LOCAL_FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)
    yield


def create_app(*, enable_startup_seed: bool = True) -> FastAPI:
    app = FastAPI(
        title="Habit Life RPG API",
        version="0.5.0",
        description="Chapter 5 local FastAPI backend for Habit Life RPG.",
        lifespan=lifespan if enable_startup_seed else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=LOCAL_FRONTEND_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(user.router)
    app.include_router(habits.router)
    return app


app = create_app()
