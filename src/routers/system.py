from fastapi import APIRouter, HTTPException, status

from src.core.database import is_db_healthy

system_router = APIRouter()


@system_router.get("/health")
async def health() -> dict[str, str]:
    """Проверка работоспособности сервиса и подключения к БД."""
    if not await is_db_healthy():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready",
        )
    return {"status": "ok"}
