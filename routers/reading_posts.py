from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies import CurrentUserDep, SessionDep
from enums import ReadingStatus
from models import ReadingPost, UserBook
from schemas.reading_posts import (
    ReadingPostCreate,
    ReadingPostResponse,
    ReadingPostUpdate,
    ReadingPostVisibilityUpdate,
)

router = APIRouter(prefix="/users/me/books", tags=["reading-posts"])


def _build_reading_post_response(
    user_book: UserBook, reading_post: ReadingPost
) -> ReadingPostResponse:
    reading_post_response = ReadingPostResponse(
        id=reading_post.id,
        recommendation_reason=reading_post.recommendation_reason,
        recommendation_score=user_book.recommendation_score,
        is_public=reading_post.is_public,
        created_at=reading_post.created_at,
    )

    return reading_post_response


@router.post(
    "/{book_id}/reading-post",
    response_model=ReadingPostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reading_post(
    book_id: int,
    reading_post_data: ReadingPostCreate,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    statement = select(UserBook).where(
        UserBook.user_id == current_user.id, UserBook.book_id == book_id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )

    if user_book.status != ReadingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="本が完読ではありません。読了投稿は完読後に可能です。",
        )

    if user_book.reading_post is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="既に読了投稿はされています。"
        )

    reading_post = ReadingPost(
        user_book_id=user_book.id,
        recommendation_reason=reading_post_data.recommendation_reason,
        is_public=reading_post_data.is_public,
    )

    db.add(reading_post)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="既に読了投稿はされています。"
        )
    db.refresh(reading_post)

    return _build_reading_post_response(user_book, reading_post)


@router.get("/{book_id}/reading-post", response_model=ReadingPostResponse)
def get_reading_post(book_id: int, db: SessionDep, current_user: CurrentUserDep):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )

    if user_book.reading_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="読了投稿がありません。"
        )

    return _build_reading_post_response(user_book, user_book.reading_post)


@router.patch("/{book_id}/reading-post", response_model=ReadingPostResponse)
def update_reading_post(
    book_id: int,
    update_reading_post_data: ReadingPostUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )
    if user_book.reading_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="読了投稿がありません。"
        )

    reading_post = user_book.reading_post
    reading_post.recommendation_reason = update_reading_post_data.recommendation_reason

    db.commit()
    db.refresh(reading_post)

    return _build_reading_post_response(user_book, reading_post)


@router.delete("/{book_id}/reading-post", status_code=status.HTTP_204_NO_CONTENT)
def delete_reading_post(book_id: int, current_user: CurrentUserDep, db: SessionDep):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )
    if user_book.reading_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="読了投稿がありません。"
        )
    reading_post = user_book.reading_post

    db.delete(reading_post)
    db.commit()


@router.patch("/{book_id}/reading-post/visibility", response_model=ReadingPostResponse)
def update_reading_post_visibility(
    book_id: int,
    reading_post_visibility_data: ReadingPostVisibilityUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )
    if user_book.reading_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="読了投稿がありません。"
        )

    reading_post = user_book.reading_post

    reading_post.is_public = reading_post_visibility_data.is_public

    db.commit()
    db.refresh(reading_post)

    return _build_reading_post_response(user_book, reading_post)
