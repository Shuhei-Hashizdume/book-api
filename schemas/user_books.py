from pydantic import BaseModel, ConfigDict, Field

from enums import ReadingPriority, ReadingStatus
from schemas.books import BookDetailResponse, BookResponse


class UserBookCreate(BaseModel):
    book_id: int = Field(gt=0)
    priority: ReadingPriority


class UserBookResponse(BaseModel):
    id: int
    book_id: int
    priority: ReadingPriority
    status: ReadingStatus
    recommendation_score: int | None


class UserBookListItem(BaseModel):
    id: int
    priority: ReadingPriority
    book: BookResponse
    status: ReadingStatus
    recommendation_score: int | None


class UserBookUpdate(BaseModel):
    priority: ReadingPriority


class UserBookStatusUpdate(BaseModel):
    status: ReadingStatus
    recommendation_score: int | None = Field(ge=1, le=5, default=None)


class UserBookFromSearchCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    external_id: str = Field(min_length=1)
    priority: ReadingPriority


class UserBookDetailResponse(BaseModel):
    book: BookDetailResponse
    is_registered: bool
    priority: ReadingPriority | None
    status: ReadingStatus | None
    recommendation_score: int | None
