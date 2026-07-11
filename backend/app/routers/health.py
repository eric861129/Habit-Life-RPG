from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.database import get_db


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/ready",
    responses={503: {"description": "Database unavailable."}},
)
def readiness(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database unavailable.") from error
    return {"status": "ready"}
