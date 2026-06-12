from collections.abc import AsyncIterator
from datetime import time

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.database import get_session
from src.core.security import hash_password
from src.main import app
from src.models.base import Base
from src.models import booking, room, time_slot, user  # noqa: F401
from src.models.room import Room
from src.models.time_slot import TimeSlot
from src.models.user import ROLE_ADMIN, User


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client

    app.dependency_overrides.clear()


@pytest.fixture
async def seeded_client(client: AsyncClient, db_session: AsyncSession) -> AsyncClient:
    test_room = Room(name="Переговорная 1")
    test_room.time_slots.append(TimeSlot(start_time=time(9, 0), end_time=time(11, 0)))
    test_room.time_slots.append(TimeSlot(start_time=time(11, 0), end_time=time(13, 0)))

    admin = User(
        email="admin@example.com",
        full_name="Администратор",
        hashed_password=hash_password("admin"),
        role=ROLE_ADMIN,
    )

    db_session.add(test_room)
    db_session.add(admin)
    await db_session.commit()

    return client
