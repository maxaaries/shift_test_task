from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.deps import get_current_user
from src.models.user import User
from src.schemas.room import RoomAvailability, RoomRead
from src.services.room_service import RoomService

rooms_router = APIRouter(prefix="/rooms", tags=["rooms"])


@rooms_router.get("", response_model=list[RoomRead])
async def list_rooms(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[RoomRead]:
    service = RoomService(session)
    return await service.list_rooms()


@rooms_router.get("/availability", response_model=list[RoomAvailability])
async def get_availability(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    booking_date: Annotated[date, Query(alias="date", description="Дата в формате YYYY-MM-DD")],
) -> list[RoomAvailability]:
    service = RoomService(session)
    return await service.get_availability(booking_date)
