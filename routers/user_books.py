from typing import Annotated

import httpx2
from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from dependencies import CurrentUserDep, SessionDep
from enums import BookGenre, ReadingStatus, UserBookListType
from models import Book, BookRating, CompletedBook, UserBook
from schemas.book_ratings import BookRatingResponse, BookRatingUpdate
from schemas.books import BookResponse
from schemas.user_books import (
    UserBookCreate,
    UserBookDetailResponse,
    UserBookFromSearchCreate,
    UserBookListItem,
    UserBookResponse,
    UserBookStatusUpdate,
    UserBookUpdate,
)
from services.book_detail import get_book_with_average_score
from services.google_books import get_google_book

router = APIRouter(prefix="/users/me/books", tags=["user-books"])


def _build_user_book_response(
    user_book: UserBook, book_rating: BookRating | None
) -> UserBookResponse:
    return UserBookResponse(
        id=user_book.id,
        book_id=user_book.book_id,
        priority=user_book.priority,
        status=user_book.status,
        recommendation_score=(
            book_rating.recommendation_score if book_rating is not None else None
        ),
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserBookResponse)
def add_book_to_user_list(
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

    book_rating_statement = select(BookRating).where(
        BookRating.user_id == current_user.id, BookRating.book_id == user_book.book_id
    )
    book_rating = db.scalar(book_rating_statement)

    return _build_user_book_response(user_book, book_rating)


@router.get("", response_model=list[UserBookListItem])
def list_user_books(
    db: SessionDep,
    current_user: CurrentUserDep,
    list_type: UserBookListType = UserBookListType.WANT_TO_READ,
):
    statement = (
        select(UserBook, BookRating.recommendation_score)
        .outerjoin(
            BookRating,
            (BookRating.book_id == UserBook.book_id)
            & (BookRating.user_id == UserBook.user_id),
        )
        .options(joinedload(UserBook.book))
        .where(UserBook.user_id == current_user.id)
    )
    if list_type == UserBookListType.COMPLETED:
        statement = statement.where(UserBook.status == ReadingStatus.COMPLETED)
    else:
        statement = statement.where(UserBook.status != ReadingStatus.COMPLETED)
    user_books = db.execute(statement).all()

    response_list = []
    for user_book, recommendation_score in user_books:
        book_response = BookResponse.model_validate(
            user_book.book,
            from_attributes=True,
        )
        user_book_list_item = UserBookListItem(
            id=user_book.id,
            priority=user_book.priority,
            status=user_book.status,
            book=book_response,
            recommendation_score=recommendation_score,
        )
        response_list.append(user_book_list_item)

    return response_list


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

    book_rating_statement = select(BookRating).where(
        BookRating.book_id == book_id, BookRating.user_id == current_user.id
    )
    book_rating = db.scalar(book_rating_statement)

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
            recommendation_score=(
                book_rating.recommendation_score if book_rating is not None else None
            ),
        )

    return UserBookDetailResponse(
        book=book_detail,
        is_registered=True,
        priority=user_book.priority,
        status=user_book.status,
        recommendation_score=(
            book_rating.recommendation_score if book_rating is not None else None
        ),
    )


@router.patch("/{book_id}/priority", response_model=UserBookResponse)
def update_user_book_priority(
    db: SessionDep,
    current_user: CurrentUserDep,
    book_id: Annotated[int, Path(gt=0)],
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

    book_rating_statement = select(BookRating).where(
        BookRating.book_id == book_id, BookRating.user_id == current_user.id
    )
    book_rating = db.scalar(book_rating_statement)

    return _build_user_book_response(user_book, book_rating)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_book(
    book_id: Annotated[int, Path(gt=0)], current_user: CurrentUserDep, db: SessionDep
):
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
    book_id: Annotated[int, Path(gt=0)],
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

    book_rating_statement = select(BookRating).where(
        BookRating.book_id == book_id, BookRating.user_id == current_user.id
    )
    book_rating = db.scalar(book_rating_statement)

    if status_data.status == ReadingStatus.COMPLETED:
        completed_book_statement = select(CompletedBook).where(
            CompletedBook.user_id == current_user.id, CompletedBook.book_id == book_id
        )

        completed_book = db.scalar(completed_book_statement)

        if completed_book is None:
            completed_book = CompletedBook(
                user_id=current_user.id,
                book_id=book_id,
            )
            db.add(completed_book)

    user_book.status = status_data.status

    if status_data.status == ReadingStatus.COMPLETED and book_rating is None:
        book_rating = BookRating(
            user_id=current_user.id,
            book_id=book_id,
            recommendation_score=status_data.recommendation_score,
        )
        db.add(book_rating)
    elif status_data.status == ReadingStatus.COMPLETED and book_rating is not None:
        book_rating.recommendation_score = status_data.recommendation_score

    db.commit()
    db.refresh(user_book)
    if book_rating is not None:
        db.refresh(book_rating)

    return _build_user_book_response(user_book, book_rating)


@router.post(
    "/from-search", status_code=status.HTTP_201_CREATED, response_model=UserBookResponse
)
def add_book_to_user_list_from_search(
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

    statement = select(Book).where(Book.external_id == google_book.external_id)
    book = db.scalar(statement)

    if book is None and google_book.isbn is not None:
        statement = select(Book).where(Book.isbn == google_book.isbn)
        book = db.scalar(statement)

    try:
        if book is None:
            book = Book(
                external_id=google_book.external_id,
                title=google_book.title,
                author=google_book.author,
                isbn=google_book.isbn,
                genre=google_book.genre,
                cover_image_url=google_book.cover_image_url,
            )
            db.add(book)
            db.flush()
        else:
            if book.genre == BookGenre.OTHER and google_book.genre != BookGenre.OTHER:
                book.genre = google_book.genre
            if book.cover_image_url is None and google_book.cover_image_url is not None:
                book.cover_image_url = google_book.cover_image_url
            if book.external_id is None:
                book.external_id = google_book.external_id

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

    book_rating_statement = select(BookRating).where(
        BookRating.book_id == user_book.book_id, BookRating.user_id == current_user.id
    )
    book_rating = db.scalar(book_rating_statement)

    return _build_user_book_response(user_book, book_rating)


@router.patch("/{book_id}/book-rating", response_model=BookRatingResponse)
def update_book_rating(
    book_rating_data: BookRatingUpdate,
    book_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUserDep,
    db: SessionDep,
):
    book_rating_statement = (
        select(BookRating)
        .options(joinedload(BookRating.book))
        .where(BookRating.book_id == book_id, BookRating.user_id == current_user.id)
    )
    book_rating = db.scalar(book_rating_statement)

    if book_rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="この本へのおすすめ度が登録されていません。",
        )

    book_rating.recommendation_score = book_rating_data.recommendation_score

    db.commit()
    db.refresh(book_rating)

    return BookRatingResponse(
        id=book_rating.id,
        book_id=book_rating.book.id,
        title=book_rating.book.title,
        recommendation_score=book_rating.recommendation_score,
    )
