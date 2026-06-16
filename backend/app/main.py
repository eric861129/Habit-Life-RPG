from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="Habit Life RPG API",
        version="0.5.0",
        description="Chapter 5 local FastAPI backend for Habit Life RPG.",
    )
    return app


app = create_app()
