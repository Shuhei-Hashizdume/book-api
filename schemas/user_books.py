from pydantic import BaseModel

from enums import ReadingPriority, ReadingStatus
from schemas.books import BookResponse


class UserBookCreate(BaseModel):
    book_id: int
    priority: ReadingPriority


class UserBookResponse(BaseModel):
    id: int
    book_id: int
    priority: ReadingPriority
    status: ReadingStatus


class UserBookListItem(BaseModel):
    id: int
    priority: ReadingPriority
    book: BookResponse
    status: ReadingStatus


class UserBookUpdate(BaseModel):
    priority: ReadingPriority


class UserBookStatusUpdate(BaseModel):
    status: ReadingStatus
