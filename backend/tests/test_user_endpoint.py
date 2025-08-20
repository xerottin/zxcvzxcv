import pytest

pytestmark = pytest.mark.asyncio


async def test_create_user_endpoint_201(client):
    resp = await client.post(
        "/api/v1/users/create",
        json={"username": None, "email": "bob@example.com", "password": "strongpass", "role": "user"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["email"] == "bob@example.com"
    assert data["id"] is not None
