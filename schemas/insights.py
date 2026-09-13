from pydantic import BaseModel, ConfigDict, Field


class InsightCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    content: str = Field(min_length=1)


class InsightResponse(BaseModel):
    id: int
    content: str


class InsightUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(min_length=1)
