from pydantic import BaseModel, ConfigDict, Field


class AISuggestionOutput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    clarified_insight: str = Field(min_length=1)
    deep_dive: str = Field(min_length=1)
    practical_application: str = Field(min_length=1)
    next_action: str = Field(min_length=1)


class AISuggestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    insight_id: int
    clarified_insight: str = Field(min_length=1)
    deep_dive: str = Field(min_length=1)
    practical_application: str = Field(min_length=1)
    next_action: str = Field(min_length=1)
