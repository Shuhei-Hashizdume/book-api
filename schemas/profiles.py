from pydantic import BaseModel

from enums import BookGenre


class PublicBookshelfBookResponse(BaseModel):
    book_id: int
    reading_post_id: int
    title: str
    author: str
    genre: BookGenre
    recommendation_score: int
    recommendation_reason: str


class UserProfileResponse(BaseModel):
    id: int
    username: str
    bio: str | None
    completed_book_count: int
    follower_count: int
    public_books: list[PublicBookshelfBookResponse]
