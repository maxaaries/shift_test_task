from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.booking_repository import BookingRepository
from src.repositories.room_repository import RoomRepository
from src.schemas.room import RoomAvailability, RoomRead, SlotAvailability


class RoomService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.room_repository = RoomRepository(session)
        self.booking_repository = BookingRepository(session)

    async def list_rooms(self) -> list[RoomRead]:
        rooms = await self.room_repository.list_with_slots()
        return [RoomRead.model_validate(room) for room in rooms]

    async def get_availability(self, booking_date: date) -> list[RoomAvailability]:
        rooms = await self.room_repository.list_with_slots()
        bookings = await self.booking_repository.list_by_date(booking_date)
        booked_slot_ids = {booking.slot_id for booking in bookings}

        result = []
        for room in rooms:
            slots = [
                SlotAvailability(
                    id=slot.id,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    is_available=slot.id not in booked_slot_ids,
                )
                for slot in sorted(room.time_slots, key=lambda item: item.start_time)
            ]
            result.append(RoomAvailability(id=room.id, name=room.name, slots=slots))

        return result
