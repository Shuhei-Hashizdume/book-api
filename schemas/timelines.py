from datetime import datetime

from pydantic import BaseModel


class TimelinePostResponse(BaseModel):
    reading_post_id: int
    user_id: int
    username: str
    book_id: int
    title: str
    recommendation_score: int
    recommendation_reason: str
    created_at: datetime
