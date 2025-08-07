from dependencies.auth import get_current_user
from fastapi import APIRouter, Depends
from models import User

router = APIRouter()


@router.get("/me")
async def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }
