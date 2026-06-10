from datetime import time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.core.security import hash_password
from src.models.room import Room
from src.models.time_slot import TimeSlot
from src.models.user import ROLE_ADMIN, User

DEFAULT_SLOTS = [
    (time(9, 0), time(11, 0)),
    (time(11, 0), time(13, 0)),
    (time(13, 0), time(16, 0)),
    (time(16, 0), time(18, 0)),
]

ROOM_NAMES = ["Переговорная 1", "Переговорная 2", "Переговорная 3"]


async def _is_db_empty(session: AsyncSession) -> bool:
    users_count = await session.scalar(select(func.count()).select_from(User))
    rooms_count = await session.scalar(select(func.count()).select_from(Room))
    return (users_count or 0) == 0 and (rooms_count or 0) == 0


async def seed_initial_data() -> None:
    """Заполняет БД начальными данными, если она пустая."""
    async with AsyncSessionLocal() as session:
        if not await _is_db_empty(session):
            return

        admin = User(
            email=settings.ADMIN_EMAIL,
            full_name=settings.ADMIN_FULL_NAME,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            role=ROLE_ADMIN,
        )
        session.add(admin)

        for room_name in ROOM_NAMES:
            new_room = Room(name=room_name)
            for start_time, end_time in DEFAULT_SLOTS:
                new_room.time_slots.append(
                    TimeSlot(start_time=start_time, end_time=end_time),
                )
            session.add(new_room)

        await session.commit()
