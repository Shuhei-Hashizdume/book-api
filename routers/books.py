from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies import AdminUserDep, SessionDep
from models import Book
from schemas.books import BookCreate, BookResponse, BookUpdate

router = APIRouter(
    prefix="/books",
    tags=["books"],
)


@router.get("/{book_id}", response_model=BookResponse)
def read_book(book_id: int, db: SessionDep):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本が見つかりません。"
        )
    return book


@router.get("", response_model=list[BookResponse])
def read_books(db: SessionDep):
    statement = select(Book)
    result = db.scalars(statement).all()
    return result


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
    book_id: int, book_data: BookUpdate, db: SessionDep, admin_user: AdminUserDep
):
    target_book = db.get(Book, book_id)
    if target_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本がありません。"
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
def delete_book(book_id: int, db: SessionDep, admin_user: AdminUserDep):
    target_book = db.get(Book, book_id)
    if target_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="本がありません。"
        )
    db.delete(target_book)
    db.commit()
