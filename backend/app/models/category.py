from beanie import Document


class Category(Document):
    name: str
    description: str | None = None

    class Settings:
        name = "categories"
