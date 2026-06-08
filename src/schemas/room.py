from datetime import date, time

from pydantic import BaseModel, ConfigDict


class TimeSlotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_time: time
    end_time: time


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    time_slots: list[TimeSlotRead]


class SlotAvailability(BaseModel):
    id: int
    start_time: time
    end_time: time
    is_available: bool


class RoomAvailability(BaseModel):
    id: int
    name: str
    slots: list[SlotAvailability]
