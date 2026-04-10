from fastapi import APIRouter

from app.api.endpoints import authors, books, categories

#APIROUTER: giúp gom tất cả các router con vào 1 router lớn.Tiện dụng khi gọi .include_router()
api_router = APIRouter()
api_router.include_router(authors.router, prefix="/authors", tags=["Authors"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(books.router, prefix="/books", tags=["Books"])

# prefix: tiền tố  URL được gắn trước tất cả route trong books.router
# Ví dụ: trong books.py có route @router.get("/") thì khi include với prefix="books"-> GET/books/
#tags : Là dùng để phân nhóm endpoint trong Swagger docs, không ảnh hưởng logic xử lý 