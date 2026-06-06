from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

__all__ = (
    "get_session",
    "init_db",
    "close_db",
    "is_db_healthy",
    "engine_async",
)


engine_async = create_async_engine(
    settings.async_database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine_async,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Проверка подключения к базе данных."""
    async with engine_async.begin() as conn:
        await conn.run_sync(lambda _: None)


async def close_db() -> None:
    await engine_async.dispose()


async def is_db_healthy() -> bool:
    try:
        async with engine_async.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
