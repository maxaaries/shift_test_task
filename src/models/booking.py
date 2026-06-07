from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Booking(BaseModel):
    __tablename__ = "bookings"
    __table_args__ = (UniqueConstraint("slot_id", "date", name="uq_booking_slot_date"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="bookings")
    time_slot: Mapped["TimeSlot"] = relationship(back_populates="bookings")
