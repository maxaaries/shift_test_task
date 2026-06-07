from datetime import time

from sqlalchemy import ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class TimeSlot(BaseModel):
    __tablename__ = "time_slots"

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    room: Mapped["Room"] = relationship(back_populates="time_slots")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="time_slot")
