from contextlib import asynccontextmanager
#asynccontextmanager: biến 1 hàm async thành contexy manager bất đồng bộ
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import FRONTEND_DIR
from app.db.mongodb import connect_db, disconnect_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    print("Connected to MongoDB")
    yield # giống như 1 điểm tạm dừng khi request đang chạy, nó sẽ chạy code dưới yield 
    #Khi nào chạy phần sau yield:1.user tắt server,2.deploy lại server
    await disconnect_db()
    print("Disconnected from MongoDB")


app = FastAPI(
    title="Book Management API",
    description="Simple API to manage books, authors, categories and book covers (MongoDB)",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
app.include_router(api_router)


@app.get("/")
def read_root():
    return RedirectResponse("/static/index.html")
