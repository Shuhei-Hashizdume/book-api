from fastapi import APIRouter

from dependencies import CurrentUserDep, SessionDep
from schemas.timelines import TimelinePostResponse
from services.timelines import get_following_timeline, get_recommended_timeline

router = APIRouter(prefix="/timeline", tags=["timelines"])


@router.get("/recommended", response_model=list[TimelinePostResponse])
def read_recommended_timeline(db: SessionDep):
    return get_recommended_timeline(db)


@router.get("/following", response_model=list[TimelinePostResponse])
def read_following_timeline(current_user: CurrentUserDep, db: SessionDep):
    return get_following_timeline(current_user.id, db)
