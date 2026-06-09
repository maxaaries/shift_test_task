from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.time_slot import TimeSlot


class TimeSlotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, slot_id: int) -> TimeSlot | None:
        return await self.session.get(TimeSlot, slot_id)

    async def list_all(self) -> list[TimeSlot]:
        stmt = select(TimeSlot).order_by(TimeSlot.room_id, TimeSlot.start_time)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
