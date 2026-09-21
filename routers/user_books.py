from typing import Annotated

import httpx2
from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from dependencies import CurrentUserDep, SessionDep
from enums import BookGenre, ReadingStatus
from models import Book, UserBook
from schemas.user_books import (
    UserBookCreate,
    UserBookDetailResponse,
    UserBookFromSearchCreate,
    UserBookListItem,
    UserBookRecommendationScoreUpdate,
    UserBookResponse,
    UserBookStatusUpdate,
    UserBookUpdate,
)
from services.book_detail import get_book_with_average_score
from services.google_books import get_google_book

router = APIRouter(prefix="/users/me/books", tags=["user-books"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserBookResponse)
def create_user_book(
    user_book_data: UserBookCreate, db: SessionDep, current_user: CurrentUserDep
):
    book = db.get(Book, user_book_data.book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="対象の本がありません。"
        )
    user_book = UserBook(
        user_id=current_user.id, book_id=book.id, priority=user_book_data.priority
    )
    db.add(user_book)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="この本は既に読みたいリストへ登録されています。",
        )
    db.refresh(user_book)

    return user_book


@router.get("", response_model=list[UserBookListItem])
def read_user_books(db: SessionDep, current_user: CurrentUserDep):
    statement = (
        select(UserBook)
        .options(joinedload(UserBook.book))
        .where(UserBook.user_id == current_user.id)
    )
    user_books = db.scalars(statement).all()
    return user_books


@router.get("/{book_id}", response_model=UserBookDetailResponse)
def get_user_book_detail(
    book_id: Annotated[int, Path(gt=0)], db: SessionDep, current_user: CurrentUserDep
):
    book_detail = get_book_with_average_score(book_id, db)

    if book_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="本が見つかりません。",
        )

    statement = select(UserBook).where(
        UserBook.user_id == current_user.id, UserBook.book_id == book_id
    )
    user_book = db.scalar(statement)

    if user_book is None:
        return UserBookDetailResponse(
            book=book_detail,
            is_registered=False,
            priority=None,
            status=None,
            recommendation_score=None,
        )

    return UserBookDetailResponse(
        book=book_detail,
        is_registered=True,
        priority=user_book.priority,
        status=user_book.status,
        recommendation_score=user_book.recommendation_score,
    )


@router.patch("/{book_id}", response_model=UserBookResponse)
def update_user_book_priority(
    db: SessionDep,
    current_user: CurrentUserDep,
    book_id: int,
    user_book_data: UserBookUpdate,
):
    statement = select(UserBook).where(
        UserBook.book_id == book_id,
        UserBook.user_id == current_user.id,
    )
    user_book = db.scalar(statement)
    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )

    user_book.priority = user_book_data.priority

    db.commit()
    db.refresh(user_book)

    return user_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_book(book_id: int, current_user: CurrentUserDep, db: SessionDep):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)
    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )
    db.delete(user_book)
    db.commit()


@router.patch("/{book_id}/status", response_model=UserBookResponse)
def update_user_book_status(
    book_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
    status_data: UserBookStatusUpdate,
):
    statement = select(UserBook).where(
        UserBook.book_id == book_id, UserBook.user_id == current_user.id
    )
    user_book = db.scalar(statement)
    if user_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません"
        )
    if (
        status_data.status == ReadingStatus.COMPLETED
        and status_data.recommendation_score is None
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="完読にするにはおすすめ度の登録が必要です。",
        )

    user_book.status = status_data.status
    user_book.recommendation_score = status_data.recommendation_score

    db.commit()
    db.refresh(user_book)

    return user_book


@router.patch("/{book_id}/recommendation-score", response_model=UserBookResponse)
def update_user_book_recommendation_score(
    recommendation_data: UserBookRecommendationScoreUpdate,
    book_id: int,
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
    if user_book.status != ReadingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="読書状態が完読でなければ、おすすめ度の変更はできません。",
        )

    user_book.recommendation_score = recommendation_data.recommendation_score

    db.commit()
    db.refresh(user_book)

    return user_book


@router.post(
    "/from-search", status_code=status.HTTP_201_CREATED, response_model=UserBookResponse
)
def create_user_book_from_search(
    user_book_data: UserBookFromSearchCreate,
    db: SessionDep,
    current_user: CurrentUserDep,
):
    try:
        google_book = get_google_book(user_book_data.external_id)
    except httpx2.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="書籍検索サービスから時間内に応答がありませんでした。",
        )
    except httpx2.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="書籍検索サービスへ接続できませんでした。",
        )
    except httpx2.HTTPStatusError as error:
        if error.response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="選択した本がGoogle Booksに存在しません。",
            )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="書籍検索サービスから正常な応答を取得できませんでした。",
        )

    if google_book is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="選択した本には登録に必要な書籍情報がありません。",
        )

    statement = select(Book).where(Book.isbn == google_book.isbn)
    book = db.scalar(statement)

    try:
        if book is None:
            book = Book(
                title=google_book.title,
                author=google_book.author,
                isbn=google_book.isbn,
                genre=google_book.genre,
            )
            db.add(book)
            db.flush()
        elif book.genre == BookGenre.OTHER and google_book.genre != BookGenre.OTHER:
            book.genre = google_book.genre

        user_book = UserBook(
            user_id=current_user.id,
            book_id=book.id,
            priority=user_book_data.priority,
        )

        db.add(user_book)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="この本は既に読みたいリストへ登録されています。",
        )

    db.refresh(user_book)
    return user_book
