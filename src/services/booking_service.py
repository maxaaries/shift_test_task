from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.booking import Booking
from src.models.user import ROLE_ADMIN, User
from src.repositories.booking_repository import BookingRepository
from src.repositories.time_slot_repository import TimeSlotRepository
from src.schemas.booking import BookingCreate, BookingRead


class BookingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.booking_repository = BookingRepository(session)
        self.time_slot_repository = TimeSlotRepository(session)

    def _to_read(self, booking: Booking) -> BookingRead:
        return BookingRead(
            id=booking.id,
            slot_id=booking.slot_id,
            date=booking.date,
            created_at=booking.created_at,
            room_name=booking.time_slot.room.name,
            start_time=booking.time_slot.start_time,
            end_time=booking.time_slot.end_time,
            user_id=booking.user_id,
        )

    async def create_booking(self, user: User, payload: BookingCreate) -> BookingRead:
        if payload.date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя бронировать прошедшую дату",
            )

        time_slot = await self.time_slot_repository.get_by_id(payload.slot_id)
        if time_slot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Слот не найден",
            )

        existing_booking = await self.booking_repository.get_by_slot_and_date(
            payload.slot_id,
            payload.date,
        )
        if existing_booking is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Слот уже занят на эту дату",
            )

        booking = Booking(
            user_id=user.id,
            slot_id=payload.slot_id,
            date=payload.date,
        )

        try:
            created_booking = await self.booking_repository.add(booking)
            await self.session.commit()
        except IntegrityError as error:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Слот уже занят на эту дату",
            ) from error

        loaded_booking = await self.booking_repository.get_by_id(created_booking.id)
        if loaded_booking is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return self._to_read(loaded_booking)

    async def list_bookings(self, user: User) -> list[BookingRead]:
        if user.role == ROLE_ADMIN:
            bookings = await self.booking_repository.list_all()
        else:
            bookings = await self.booking_repository.list_by_user(user.id)

        return [self._to_read(booking) for booking in bookings]

    async def cancel_booking(self, user: User, booking_id: int) -> None:
        booking = await self.booking_repository.get_by_id(booking_id)
        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Бронирование не найдено",
            )

        if user.role != ROLE_ADMIN and booking.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для отмены бронирования",
            )

        await self.booking_repository.delete(booking)
        await self.session.commit()
