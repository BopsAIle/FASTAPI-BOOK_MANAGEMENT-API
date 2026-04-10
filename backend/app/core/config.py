import os
from pathlib import Path

from pydantic import BaseModel, Field
# Path(): tạo 1 đối tượng Path đường dẫn
#__file__: lấy đường dẫn hiện tại của file -> :D/FastAPI_BOOK_MANAGEMENT/backend/app/api/core/config.py
#resolve() :Chuyển thành đường dẫn tuyệt đối
# parents[i]: Lấy đường dẫn cha thứ i(0 là /core)
REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = REPO_ROOT / "frontend"
COVERS_DIR = FRONTEND_DIR / "covers"


class Settings(BaseModel):
    PROJECT_NAME: str = "Book Management API"
    MONGODB_URI: str = Field(
        default_factory=lambda: os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
        description="MongoDB connection URI",
    )
    MONGODB_DB_NAME: str = Field(
        default_factory=lambda: os.environ.get("MONGODB_DB_NAME", "book_management"),
        description="Database name",
    )


settings = Settings()
