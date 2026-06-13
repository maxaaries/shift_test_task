import pytest
from httpx import AsyncClient


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
async def test_register_and_login(seeded_client: AsyncClient) -> None:
    response = await seeded_client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "full_name": "Новый пользователь",
            "password": "secret",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "employee"

    response = await seeded_client.post(
        "/auth/login",
        data={"username": "newuser@example.com", "password": "secret"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
