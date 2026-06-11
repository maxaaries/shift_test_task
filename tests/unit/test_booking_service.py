from datetime import date, datetime, time
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from src.models.user import ROLE_ADMIN, ROLE_EMPLOYEE, User
from src.schemas.booking import BookingCreate
from src.services.booking_service import BookingService


def make_booking_mock(
    booking_id: int = 1,
    user_id: int = 1,
    slot_id: int = 1,
    booking_date: date | None = None,
) -> MagicMock:
    booking = MagicMock()
    booking.id = booking_id
    booking.user_id = user_id
    booking.slot_id = slot_id
    booking.date = booking_date or date.today()
    booking.created_at = datetime(2026, 6, 15, 10, 0, 0)
    booking.time_slot.room.name = "Переговорная 1"
    booking.time_slot.start_time = time(9, 0)
    booking.time_slot.end_time = time(11, 0)
    return booking


@pytest.mark.asyncio
async def test_create_booking_success() -> None:
    session = AsyncMock()
    service = BookingService(session)

    service.time_slot_repository = AsyncMock()
    service.time_slot_repository.get_by_id.return_value = MagicMock(id=1)

    booking_mock = make_booking_mock()
    service.booking_repository = AsyncMock()
    service.booking_repository.get_by_slot_and_date.return_value = None
    service.booking_repository.add.return_value = booking_mock
    service.booking_repository.get_by_id.return_value = booking_mock

    user = User(
        id=1,
        email="user@test.com",
        full_name="User",
        hashed_password="hash",
        role=ROLE_EMPLOYEE,
    )
    result = await service.create_booking(
        user,
        BookingCreate(slot_id=1, date=date.today()),
    )

    assert result.id == 1
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_booking_slot_taken() -> None:
    session = AsyncMock()
    service = BookingService(session)

    service.time_slot_repository = AsyncMock()
    service.time_slot_repository.get_by_id.return_value = MagicMock(id=1)

    service.booking_repository = AsyncMock()
    service.booking_repository.get_by_slot_and_date.return_value = object()

    user = User(
        id=1,
        email="user@test.com",
        full_name="User",
        hashed_password="hash",
        role=ROLE_EMPLOYEE,
    )

    with pytest.raises(HTTPException) as error:
        await service.create_booking(
            user,
            BookingCreate(slot_id=1, date=date.today()),
        )

    assert error.value.status_code == 409


@pytest.mark.asyncio
async def test_cancel_own_booking() -> None:
    session = AsyncMock()
    service = BookingService(session)

    booking_mock = make_booking_mock(user_id=1)
    service.booking_repository = AsyncMock()
    service.booking_repository.get_by_id.return_value = booking_mock

    user = User(
        id=1,
        email="user@test.com",
        full_name="User",
        hashed_password="hash",
        role=ROLE_EMPLOYEE,
    )

    await service.cancel_booking(user, 1)
    service.booking_repository.delete.assert_awaited_once_with(booking_mock)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_cancel_other_user_booking_forbidden() -> None:
    session = AsyncMock()
    service = BookingService(session)

    service.booking_repository = AsyncMock()
    service.booking_repository.get_by_id.return_value = make_booking_mock(user_id=2)

    user = User(
        id=1,
        email="user@test.com",
        full_name="User",
        hashed_password="hash",
        role=ROLE_EMPLOYEE,
    )

    with pytest.raises(HTTPException) as error:
        await service.cancel_booking(user, 1)

    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_admin_cancel_any_booking() -> None:
    session = AsyncMock()
    service = BookingService(session)

    booking_mock = make_booking_mock(user_id=2)
    service.booking_repository = AsyncMock()
    service.booking_repository.get_by_id.return_value = booking_mock

    admin = User(
        id=1,
        email="admin@test.com",
        full_name="Admin",
        hashed_password="hash",
        role=ROLE_ADMIN,
    )

    await service.cancel_booking(admin, 1)
    service.booking_repository.delete.assert_awaited_once_with(booking_mock)
