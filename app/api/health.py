from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.session import test_db_connection

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "api"}


@router.get("/health/db")
def db_health_check() -> JSONResponse:
    ok, message = test_db_connection()

    if ok:
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "db_status": "connected", "message": message},
        )

    return JSONResponse(
        status_code=503,
        content={"status": "degraded", "db_status": "disconnected", "message": message},
    )
