from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.database import close_db, init_db
from src.routers.system import system_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    lifespan=lifespan,
    title=f"{settings.APP_NAME} API",
    version="1.0.0",
)

app.include_router(system_router)
