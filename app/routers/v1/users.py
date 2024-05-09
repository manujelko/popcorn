from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_current_active_user
from app.models.users import User, UserPublic

router = APIRouter(prefix="/users")


@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
