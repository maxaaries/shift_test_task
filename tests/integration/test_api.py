from datetime import date

import pytest
from httpx import AsyncClient


async def register_and_login(
    client: AsyncClient,
    email: str,
    full_name: str,
    password: str,
) -> str:
    response = await client.post(
        "/auth/register",
        json={"email": email, "full_name": full_name, "password": password},
    )
    assert response.status_code == 201

    response = await client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_request_without_token_returns_401(client: AsyncClient) -> None:
    response = await client.get("/rooms")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_request_with_invalid_token_returns_401(client: AsyncClient) -> None:
    response = await client.get(
        "/rooms",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_booking_flow(seeded_client: AsyncClient) -> None:
    token = await register_and_login(
        seeded_client,
        "user@example.com",
        "Пользователь",
        "secret",
    )
    headers = {"Authorization": f"Bearer {token}"}
    booking_date = date.today().isoformat()

    rooms_response = await seeded_client.get("/rooms", headers=headers)
    assert rooms_response.status_code == 200
    slot_id = rooms_response.json()[0]["time_slots"][0]["id"]

    availability_before = await seeded_client.get(
        f"/rooms/availability?date={booking_date}",
        headers=headers,
    )
    assert availability_before.status_code == 200
    assert availability_before.json()[0]["slots"][0]["is_available"] is True

    create_response = await seeded_client.post(
        "/bookings",
        headers=headers,
        json={"slot_id": slot_id, "date": booking_date},
    )
    assert create_response.status_code == 201
    booking_id = create_response.json()["id"]

    availability_after = await seeded_client.get(
        f"/rooms/availability?date={booking_date}",
        headers=headers,
    )
    assert availability_after.json()[0]["slots"][0]["is_available"] is False

    list_response = await seeded_client.get("/bookings", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    delete_response = await seeded_client.delete(
        f"/bookings/{booking_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_user_cannot_see_or_cancel_other_booking(seeded_client: AsyncClient) -> None:
    user_a_token = await register_and_login(
        seeded_client,
        "usera@example.com",
        "User A",
        "secret",
    )
    user_b_token = await register_and_login(
        seeded_client,
        "userb@example.com",
        "User B",
        "secret",
    )

    rooms_response = await seeded_client.get(
        "/rooms",
        headers={"Authorization": f"Bearer {user_a_token}"},
    )
    slot_id = rooms_response.json()[0]["time_slots"][0]["id"]
    booking_date = date.today().isoformat()

    create_response = await seeded_client.post(
        "/bookings",
        headers={"Authorization": f"Bearer {user_a_token}"},
        json={"slot_id": slot_id, "date": booking_date},
    )
    booking_id = create_response.json()["id"]

    user_b_bookings = await seeded_client.get(
        "/bookings",
        headers={"Authorization": f"Bearer {user_b_token}"},
    )
    assert user_b_bookings.status_code == 200
    assert user_b_bookings.json() == []

    cancel_response = await seeded_client.delete(
        f"/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {user_b_token}"},
    )
    assert cancel_response.status_code == 403
