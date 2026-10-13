from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies import CurrentUserDep, SessionDep
from models import Like, ReadingPost
from schemas.likes import LikeResponse

router = APIRouter(prefix="/reading-posts", tags=["likes"])


@router.post(
    "/{reading_post_id}/likes",
    status_code=status.HTTP_201_CREATED,
    response_model=LikeResponse,
)
def create_like(
    reading_post_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    db: SessionDep,
):
    statement = select(ReadingPost).where(ReadingPost.id == reading_post_id)
    reading_post = db.scalar(statement)

    if reading_post is None or not reading_post.is_public:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="読了投稿が見つかりません。",
        )
    if reading_post.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="自分の投稿へいいね!はできません。",
        )

    like_statement = select(Like).where(
        Like.user_id == current_user.id, Like.reading_post_id == reading_post_id
    )
    existing_like = db.scalar(like_statement)

    if existing_like is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="読了投稿に既にいいね！があります。",
        )

    like = Like(user_id=current_user.id, reading_post_id=reading_post_id)

    db.add(like)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="読了投稿に既にいいね！があります。",
        )

    db.refresh(like)
    return like


@router.delete("/{reading_post_id}/likes", status_code=status.HTTP_204_NO_CONTENT)
def delete_like(
    reading_post_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    db: SessionDep,
):
    statement = select(ReadingPost).where(ReadingPost.id == reading_post_id)
    reading_post = db.scalar(statement)

    if reading_post is None or not reading_post.is_public:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="読了投稿が見つかりません。",
        )

    like_statement = select(Like).where(
        Like.reading_post_id == reading_post_id, Like.user_id == current_user.id
    )
    like = db.scalar(like_statement)

    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="読了投稿へのいいね！が見つかりません。",
        )

    db.delete(like)
    db.commit()
