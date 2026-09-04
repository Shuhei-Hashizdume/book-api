from fastapi import APIRouter, status

from dependencies import SessionDep
from models import Book
from schemas import BookCreate

router = APIRouter(
    prefix="/books",
    tags=["books"],
)


books = [
    {
        "id": 1,
        "title": "GANTZ 1",
        "author": "奥 浩哉",
        "isbn": "978-4-08-876105-3",
    },
    {
        "id": 2,
        "title": "嫌われる勇気",
        "author": "岸見 一郎、古賀 史健",
        "isbn": "978-4-478-02581-9",
    },
    {
        "id": 3,
        "title": "メモの魔力",
        "author": "前田 裕二",
        "isbn": "978-4-344-03408-2",
    },
]


@router.get("/1")
def read_book():
    return books[0]


@router.get("")
def read_books():
    return books


@router.post("", status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookCreate, db: SessionDep):
    book = Book(
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
    )

    db.add(book)
    db.commit()
    db.refresh(book)
    return book
