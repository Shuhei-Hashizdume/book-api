from datetime import datetime

from pydantic import BaseModel


class LikeResponse(BaseModel):
    id: int
    user_id: int
    reading_post_id: int
    created_at: datetime
