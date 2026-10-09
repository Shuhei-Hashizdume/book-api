from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from enums import BookGenre


class BookCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    isbn: str | None = Field(default=None, pattern=r"^\d{13}$")


class BookUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(min_length=1, max_length=255, default=None)
    author: str | None = Field(min_length=1, max_length=255, default=None)
    isbn: str | None = Field(default=None, pattern=r"^\d{13}$")

    @field_validator("title", "author")
    @classmethod
    def reject_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("nullは指定できません。")
        return value

    @model_validator(mode="after")
    def require_update_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("更新する項目を1つ以上指定してください。")
        return self


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    cover_image_url: str | None


class BookSearchResult(BaseModel):
    external_id: str
    title: str
    author: str
    isbn: str | None
    genre: BookGenre
    cover_image_url: str | None


class BookDetailResponse(BookResponse):
    genre: BookGenre
    average_recommendation_score: float | None


class RelatedBookResponse(BaseModel):
    book_id: int
    title: str
    cover_image_url: str | None
    average_recommendation_score: float | None
