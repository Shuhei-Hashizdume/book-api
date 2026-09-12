from pydantic import BaseModel, Field

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


class UserBookRecommendationScoreUpdate(BaseModel):
    recommendation_score: int = Field(ge=1, le=5)
