from datetime import date

import pytest
from httpx import AsyncClient

from tests.integration.helpers import register_and_login


@pytest.mark.asyncio
async def test_list_rooms(seeded_client: AsyncClient) -> None:
    token = await register_and_login(
        seeded_client,
        "rooms@example.com",
        "Пользователь",
        "secret",
    )

    response = await seeded_client.get(
        "/rooms",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    rooms = response.json()
    assert len(rooms) == 1
    assert rooms[0]["name"] == "Переговорная 1"
    assert len(rooms[0]["time_slots"]) == 2


@pytest.mark.asyncio
async def test_availability_shows_free_slots(seeded_client: AsyncClient) -> None:
    token = await register_and_login(
        seeded_client,
        "availability@example.com",
        "Пользователь",
        "secret",
    )
    booking_date = date.today().isoformat()

    response = await seeded_client.get(
        f"/rooms/availability?date={booking_date}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    slots = response.json()[0]["slots"]
    assert all(slot["is_available"] for slot in slots)
