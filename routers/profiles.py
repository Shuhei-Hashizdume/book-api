from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from dependencies import SessionDep
from schemas.profiles import UserProfileResponse
from services.profile import get_user_profile

router = APIRouter(prefix="/users", tags=["profiles"])


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
def read_user_profile(user_id: Annotated[int, Path(gt=0)], db: SessionDep):
    user_profile = get_user_profile(user_id, db)

    if user_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません。"
        )

    return user_profile
