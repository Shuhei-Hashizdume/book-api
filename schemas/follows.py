from datetime import datetime

from pydantic import BaseModel


class FollowResponse(BaseModel):
    id: int
    follower_id: int
    followed_id: int
    created_at: datetime
