from pydantic import BaseModel, Field


class BookRatingUpdate(BaseModel):
    recommendation_score: int = Field(ge=1, le=5)


class BookRatingResponse(BaseModel):
    id: int
    book_id: int
    title: str
    recommendation_score: int
