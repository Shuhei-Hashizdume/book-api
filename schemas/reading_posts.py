from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReadingPostCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    recommendation_reason: str = Field(min_length=1, max_length=1000)
    is_public: bool = Field(default=True)


class ReadingPostResponse(BaseModel):
    id: int
    recommendation_reason: str
    recommendation_score: int
    is_public: bool
    created_at: datetime


class ReadingPostUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    recommendation_reason: str = Field(min_length=1, max_length=1000)


class ReadingPostVisibilityUpdate(BaseModel):
    is_public: bool
