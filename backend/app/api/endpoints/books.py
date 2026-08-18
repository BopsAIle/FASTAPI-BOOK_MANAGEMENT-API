import uuid
from datetime import datetime, timezone
from pathlib import Path

from beanie import PydanticObjectId
from beanie.operators import And, In, Or, RegEx
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.api.deps import parse_object_id
from app.core.config import COVERS_DIR
from app.models import Author, Book, Category
from app.schemas.author import Author as AuthorSchema
from app.schemas.book import Book as BookSchema
from app.schemas.book import BookCreate, BookUpdate
from app.schemas.category import Category as CategorySchema

router = APIRouter()

COVERS_DIR.mkdir(parents=True, exist_ok=True)


def _author_schema(doc: Author) -> AuthorSchema:
    return AuthorSchema(id=str(doc.id), name=doc.name, bio=doc.bio)


def _category_schema(doc: Category) -> CategorySchema:
    return CategorySchema(id=str(doc.id), name=doc.name, description=doc.description)


async def _book_schema(book: Book, author: Author, category: Category) -> BookSchema:
    return BookSchema(
        id=str(book.id),
        title=book.title,
        description=book.description,
        published_year=book.published_year,
        price=book.price,
        author_id=str(book.author_id),
        category_id=str(book.category_id),
        cover_image=book.cover_image,
        created_at=book.created_at,
        updated_at=book.updated_at,
        author=_author_schema(author),
        category=_category_schema(category),
    )


async def _load_books_with_relations(books: list[Book]) -> list[BookSchema]:
    if not books:
        return []
    author_ids = list({b.author_id for b in books})
    category_ids = list({b.category_id for b in books})
    authors = await Author.find(In(Author.id, author_ids)).to_list()
    categories = await Category.find(In(Category.id, category_ids)).to_list()
    amap = {a.id: a for a in authors}
    cmap = {c.id: c for c in categories}
    out: list[BookSchema] = []
    for b in books:
        a = amap.get(b.author_id)
        c = cmap.get(b.category_id)
        if not a or not c:
            continue
        out.append(await _book_schema(b, a, c))
    return out


async def _get_book_with_relations(book_id: PydanticObjectId) -> tuple[Book, Author, Category] | None:
    book = await Book.get(book_id)
    if not book:
        return None
    author = await Author.get(book.author_id)
    category = await Category.get(book.category_id)
    if not author or not category:
        return None
    return book, author, category


@router.get("/", response_model=list[BookSchema])
async def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    author_id: str | None = Query(None),
    category_id: str | None = Query(None),
    year: int | None = Query(None),
    keyword: str | None = Query(None),
):
    parts = []
    if author_id is not None:
        parts.append(Book.author_id == parse_object_id(author_id))
    if category_id is not None:
        parts.append(Book.category_id == parse_object_id(category_id))
    if year is not None:
        parts.append(Book.published_year == year)
    if keyword is not None and keyword.strip():
        kw = keyword.strip()
        parts.append(Or(RegEx(Book.title, kw, "i"), RegEx(Book.description, kw, "i")))

    q = Book.find(And(*parts)) if parts else Book.find_all()
    books = await q.sort(-Book.created_at).skip(skip).limit(limit).to_list()
    return await _load_books_with_relations(books)


@router.get("/{book_id}", response_model=BookSchema)
async def get_book(book_id: str):
    oid = parse_object_id(book_id)
    loaded = await _get_book_with_relations(oid)
    if not loaded:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    book, author, category = loaded
    return await _book_schema(book, author, category)


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(book_in: BookCreate):
    a_oid = parse_object_id(book_in.author_id)
    c_oid = parse_object_id(book_in.category_id)
    author = await Author.get(a_oid)
    if not author:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author does not exist")
    category = await Category.get(c_oid)
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist")

    book = Book(
        title=book_in.title,
        description=book_in.description,
        published_year=book_in.published_year,
        price=book_in.price,
        author_id=a_oid,
        category_id=c_oid,
    )
    await book.insert()
    return await _book_schema(book, author, category)


@router.put("/{book_id}", response_model=BookSchema)
async def update_book(book_id: str, book_up: BookUpdate):
    oid = parse_object_id(book_id)
    loaded = await _get_book_with_relations(oid)
    if not loaded:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    book, author, category = loaded

    if book_up.title is not None:
        book.title = book_up.title
    if book_up.description is not None:
        book.description = book_up.description
    if book_up.published_year is not None:
        book.published_year = book_up.published_year
    if book_up.price is not None:
        book.price = book_up.price

    if book_up.author_id is not None:
        new_a = parse_object_id(book_up.author_id)
        na = await Author.get(new_a)
        if not na:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New author does not exist",
            )
        book.author_id = new_a
        author = na

    if book_up.category_id is not None:
        new_c = parse_object_id(book_up.category_id)
        nc = await Category.get(new_c)
        if not nc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New category does not exist",
            )
        book.category_id = new_c
        category = nc

    book.updated_at = datetime.now(timezone.utc)
    await book.save()
    return await _book_schema(book, author, category)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str):
    oid = parse_object_id(book_id)
    book = await Book.get(oid)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    await book.delete()


@router.post("/{book_id}/cover", response_model=BookSchema)
async def upload_book_cover(
    book_id: str,
    file: UploadFile = File(...),
):
    oid = parse_object_id(book_id)
    loaded = await _get_book_with_relations(oid)
    if not loaded:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    book, author, category = loaded

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image type. Only JPEG and PNG are allowed.",
        )

    ext = Path(file.filename or "").suffix.lower()
    if ext not in [".jpeg", ".png", ".jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image type. Only .jpg, .jpeg, .png are allowed.",
        )

    contents = await file.read()
    max_size = 2 * 1024 * 1024
    if len(contents) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File to large. Max size is 2MB",
        )

    filename = f"book_{book_id}_{uuid.uuid4().hex}{ext}"
    file_path = COVERS_DIR / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    book.cover_image = f"/static/covers/{filename}"
    book.updated_at = datetime.now(timezone.utc)
    await book.save()

    return await _book_schema(book, author, category)
