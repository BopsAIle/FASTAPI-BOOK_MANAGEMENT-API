from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Book(Document):
    title: str
    description: str | None = None
    published_year: int
    author_id: PydanticObjectId
    category_id: PydanticObjectId
    cover_image: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "books"
