import pytest
from crud.user import create_user
from models.user import User
from schemas.user import UserCreate
from sqlalchemy import select

pytestmark = pytest.mark.asyncio


async def test_create_user_persists_to_db(db_session):
    payload = UserCreate(
        username=None, email="alice@example.com", password="secret", role="user"
    )
    user = await create_user(db_session, payload)
    assert user.id is not None
    assert user.email == "alice@example.com"
    assert user.username

    q = await db_session.execute(select(User).where(User.id == user.id))
    saved = q.scalar_one()
    assert saved.email == "alice@example.com"


async def test_create_user_duplicate_email_409(db_session):
    p1 = UserCreate(username="u1", email="dup@example.com", password="xx", role="user")
    await create_user(db_session, p1)

    p2 = UserCreate(username="u2", email="dup@example.com", password="xy", role="user")

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await create_user(db_session, p2)
    assert exc.value.status_code == 409
