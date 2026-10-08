from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FollowResponse(BaseModel):
    id: int
    follower_id: int
    followed_id: int
    created_at: datetime


class ShowFollowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
