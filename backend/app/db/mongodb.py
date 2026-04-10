from beanie import init_beanie
from pymongo import AsyncMongoClient # AsyncMongoClient: là 1 MongoDB client kết nối trực tiếp với MongoDB
# gửi query tới database

from app.core.config import settings
###Đây là các bảng model của database
from app.models.author import Author
from app.models.book import Book
from app.models.category import Category

_client: AsyncMongoClient | None = None
#Đây là code base của sự kết hợp AsyncMongoClient và Beanie
# async def connect_db():
#     client = AsyncMongoClient("mongodb://...")
#     db = client["mydb"]

#     await init_beanie(database=db, document_models=[User])
async def connect_db() -> None:
    global _client
    #Khai báo client :  client = AsyncMongoClient(URL đến database), là 1 object
    _client = AsyncMongoClient(settings.MONGODB_URI)
    #
    await init_beanie(
        database=_client[settings.MONGODB_DB_NAME],
        document_models=[Author, Category, Book], #các bảng được import từ models.py
    )


async def disconnect_db() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
