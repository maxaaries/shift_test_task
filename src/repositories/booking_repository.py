from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.booking import Booking
from src.models.time_slot import TimeSlot


class BookingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, booking_id: int) -> Booking | None:
        stmt = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(
                selectinload(Booking.time_slot).selectinload(TimeSlot.room),
                selectinload(Booking.user),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slot_and_date(self, slot_id: int, booking_date: date) -> Booking | None:
        stmt = select(Booking).where(
            Booking.slot_id == slot_id,
            Booking.date == booking_date,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[Booking]:
        stmt = (
            select(Booking)
            .where(Booking.user_id == user_id)
            .options(
                selectinload(Booking.time_slot).selectinload(TimeSlot.room),
            )
            .order_by(Booking.date, Booking.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_all(self) -> list[Booking]:
        stmt = (
            select(Booking)
            .options(
                selectinload(Booking.time_slot).selectinload(TimeSlot.room),
            )
            .order_by(Booking.date, Booking.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_by_date(self, booking_date: date) -> list[Booking]:
        stmt = select(Booking).where(Booking.date == booking_date)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, booking: Booking) -> Booking:
        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking

    async def delete(self, booking: Booking) -> None:
        await self.session.delete(booking)
