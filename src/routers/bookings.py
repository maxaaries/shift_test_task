from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.deps import get_current_user
from src.models.user import User
from src.schemas.booking import BookingCreate, BookingRead
from src.services.booking_service import BookingService

bookings_router = APIRouter(prefix="/bookings", tags=["bookings"])


@bookings_router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BookingRead:
    service = BookingService(session)
    return await service.create_booking(current_user, payload)


@bookings_router.get("", response_model=list[BookingRead])
async def list_bookings(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[BookingRead]:
    service = BookingService(session)
    return await service.list_bookings(current_user)


@bookings_router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    service = BookingService(session)
    await service.cancel_booking(current_user, booking_id)
