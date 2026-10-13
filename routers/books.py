from typing import Annotated

import httpx2
from fastapi import APIRouter, HTTPException, Path, status
from pydantic import StringConstraints
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies import AdminUserDep, SessionDep
from models import Book
from schemas.books import (
    BookCreate,
    BookDetailResponse,
    BookResponse,
    BookSearchResult,
    BookUpdate,
    RelatedBookResponse,
)
from services.book_detail import get_book_with_average_score
from services.google_books import search_google_books
from services.related_books import get_related_books

router = APIRouter(
    prefix="/books",
    tags=["books"],
)


@router.get("/search", response_model=list[BookSearchResult])
def search_books(
    q: Annotated[
        str,
        StringConstraints(
            min_length=1,
            strip_whitespace=True,
        ),
    ],
):
    try:
        return search_google_books(q)
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
    except httpx2.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="書籍検索サービスから正常な応答を取得できませんでした。",
        )


@router.get("/{book_id}", response_model=BookDetailResponse)
def get_book_detail(book_id: Annotated[int, Path(gt=0)], db: SessionDep):
    book_detail = get_book_with_average_score(book_id, db)
    if book_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )
    return book_detail


@router.get("", response_model=list[BookResponse])
def list_books(db: SessionDep):
    statement = select(Book)
    result = db.scalars(statement).all()
    return result


@router.get("/{book_id}/related", response_model=list[RelatedBookResponse])
def list_related_books(book_id: Annotated[int, Path(gt=0)], db: SessionDep):
    related_books = get_related_books(book_id, db)

    if related_books is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="本が見つかりません。",
        )

    return related_books


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BookResponse)
def create_book(book_data: BookCreate, db: SessionDep, admin_user: AdminUserDep):
    book = Book(
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
    )
    db.add(book)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="同じISBNの本が既に登録されています。",
        )
    db.refresh(book)
    return book


@router.patch("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: Annotated[int, Path(gt=0)],
    book_data: BookUpdate,
    db: SessionDep,
    admin_user: AdminUserDep,
):
    target_book = db.get(Book, book_id)
    if target_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target_book, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="同じISBNの本が既に登録されています。",
        )
    db.refresh(target_book)
    return target_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: Annotated[int, Path(gt=0)], db: SessionDep, admin_user: AdminUserDep
):
    target_book = db.get(Book, book_id)
    if target_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )
    db.delete(target_book)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="この本はユーザーの記録で使用されているため、削除できません。",
        )
