from typing import Annotated

from beanie import Document, Indexed


class User(Document):
    email: Annotated[str, Indexed(unique=True)]
    hashed_password: str
    full_name: str | None = None
    is_active: bool = True

    class Settings:
        name = "users"
