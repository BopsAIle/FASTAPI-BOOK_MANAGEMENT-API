# Đây là class Beanie Document, mô tả 1 document trong MongoDB




from beanie import Document


class Author(Document):
    name: str
    bio: str | None = None

    class Settings:
        name = "authors"
