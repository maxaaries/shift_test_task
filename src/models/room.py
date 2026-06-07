from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Room(BaseModel):
    __tablename__ = "rooms"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    time_slots: Mapped[list["TimeSlot"]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan",
    )
