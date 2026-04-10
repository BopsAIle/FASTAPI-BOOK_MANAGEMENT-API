from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import parse_object_id
from app.models import Author, Book # Các model đây là định nghĩa cấu trúc của 1 document sẽ lưu trong MôngĐB
from app.schemas.author import Author as AuthorSchema 
from app.schemas.author import AuthorCreate, AuthorUpdate

router = APIRouter()


def _author_schema(doc: Author) -> AuthorSchema:
    return AuthorSchema(id=str(doc.id), name=doc.name, bio=doc.bio)


@router.get("/", response_model=list[AuthorSchema])
async def list_authors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    authors = await Author.find_all().skip(skip).limit(limit).to_list()
    return [_author_schema(a) for a in authors]


@router.get("/{author_id}", response_model=AuthorSchema)
async def get_author(author_id: str):
    oid = parse_object_id(author_id)
    author = await Author.get(oid)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return _author_schema(author)


@router.post("/", response_model=AuthorSchema, status_code=status.HTTP_201_CREATED)
async def create_author(author_in: AuthorCreate):
    existing = await Author.find_one(Author.name == author_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author with this name already exists",
        )
    author = Author(name=author_in.name, bio=author_in.bio)
    await author.insert() # insert 1 document vào MongoDB
    return _author_schema(author)


@router.put("/{author_id}", response_model=AuthorSchema)
async def update_author(author_id: str, author_up: AuthorUpdate):
    oid = parse_object_id(author_id)
    author = await Author.get(oid)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="author not found")

    if author_up.name is not None and author_up.name != author.name:
        existing = await Author.find_one(Author.name == author_up.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another author with this name already exists",
            )
        author.name = author_up.name

    if author_up.bio is not None:
        author.bio = author_up.bio

    await author.save() #Lưu  document vào MogoDB sau khi sửa
    return _author_schema(author)


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(author_id: str):
    oid = parse_object_id(author_id)
    author = await Author.get(oid)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    linked = await Book.find(Book.author_id == oid).count()
    if linked > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete author with related books",
        )

    await author.delete()
