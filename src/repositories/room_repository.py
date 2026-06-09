from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.room import Room


class RoomRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_with_slots(self) -> list[Room]:
        stmt = select(Room).options(selectinload(Room.time_slots)).order_by(Room.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_id(self, room_id: int) -> Room | None:
        return await self.session.get(Room, room_id)
