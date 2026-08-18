from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.author import Author
from app.schemas.category import Category


class BookBase(BaseModel):
    title: str
    description: str | None = None
    published_year: int
    price: int = Field(..., ge=0, description="Giá sách (VND)")
    category_id: str
    author_id: str


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    published_year: int | None = None
    price: int | None = Field(None, ge=0, description="Giá sách (VND)")
    category_id: str | None = None
    author_id: str | None = None


class BookInDBBase(BookBase):
    id: str
    cover_image: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Book(BookInDBBase):
    author: Author
    category: Category
