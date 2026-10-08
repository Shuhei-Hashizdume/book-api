from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies import CurrentUserDep, SessionDep
from models import Follow, User
from schemas.follows import FollowResponse, ShowFollowResponse

router = APIRouter(prefix="/users", tags=["follows"])


@router.post(
    "/{followed_user_id}/follow",
    response_model=FollowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_follow(followed_user_id: int, current_user: CurrentUserDep, db: SessionDep):
    statement = select(User).where(User.id == followed_user_id)
    user = db.scalar(statement)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません。"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="自分自身をフォローはできません。",
        )

    follow_statement = select(Follow).where(
        Follow.followed_id == followed_user_id, Follow.follower_id == current_user.id
    )
    existing_follow = db.scalar(follow_statement)
    if existing_follow is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="既にフォローしています。"
        )

    follow = Follow(
        follower_id=current_user.id,
        followed_id=followed_user_id,
    )

    db.add(follow)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="既にフォローしています。"
        )

    db.refresh(follow)
    return follow


@router.delete("/{followed_user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def delete_follow(followed_user_id: int, current_user: CurrentUserDep, db: SessionDep):
    user_statement = select(User).where(User.id == followed_user_id)
    user = db.scalar(user_statement)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません。",
        )

    existing_follow_statement = select(Follow).where(
        Follow.followed_id == followed_user_id, Follow.follower_id == current_user.id
    )
    existing_follow = db.scalar(existing_follow_statement)

    if existing_follow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーをフォローしていません。",
        )

    db.delete(existing_follow)
    db.commit()


@router.get("/me/following", response_model=list[ShowFollowResponse])
def read_following_users(current_user: CurrentUserDep, db: SessionDep):
    statement = (
        select(User)
        .join(Follow, Follow.followed_id == User.id)
        .where(Follow.follower_id == current_user.id)
    )

    following_users = db.scalars(statement).all()
    return following_users


@router.get("/me/followers", response_model=list[ShowFollowResponse])
def read_follower_users(current_user: CurrentUserDep, db: SessionDep):
    statement = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.followed_id == current_user.id)
    )

    follower_users = db.scalars(statement).all()
    return follower_users
