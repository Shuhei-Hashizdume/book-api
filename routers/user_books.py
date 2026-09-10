from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from dependencies import CurrentUserDep, SessionDep
from models import Book, UserBook
from schemas.user_books import (
    UserBookCreate,
    UserBookListItem,
    UserBookResponse,
    UserBookUpdate,
)

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
