from pydantic import BaseModel

from enums import ReadingPriority
from schemas.books import BookResponse


class UserBookCreate(BaseModel):
    book_id: int
    priority: ReadingPriority


class UserBookResponse(BaseModel):
    id: int
    book_id: int
    priority: ReadingPriority


class UserBookListItem(BaseModel):
    id: int
    priority: ReadingPriority
    book: BookResponse


class UserBookUpdate(BaseModel):
    priority: ReadingPriority
