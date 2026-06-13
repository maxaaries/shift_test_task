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
