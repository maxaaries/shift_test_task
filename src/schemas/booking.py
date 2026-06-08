from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class BookingCreate(BaseModel):
    slot_id: int
    date: date


class BookingRead(BaseModel):
    id: int
    slot_id: int
    date: date
    created_at: datetime
    room_name: str
    start_time: time
    end_time: time
    user_id: int
