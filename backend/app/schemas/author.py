from pydantic import BaseModel, ConfigDict


class AuthorBase(BaseModel):
    name: str
    bio: str | None = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None


class AuthorInDBBase(AuthorBase):
    id: str

    model_config = ConfigDict(from_attributes=True)


class Author(AuthorInDBBase):
    pass
