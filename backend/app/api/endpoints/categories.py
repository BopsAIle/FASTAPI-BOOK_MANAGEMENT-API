from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import parse_object_id
from app.models import Book, Category
from app.schemas.category import Category as CategorySchema
from app.schemas.category import CategoryCreate, CategoryUpdate

router = APIRouter()


def _category_schema(doc: Category) -> CategorySchema:
    return CategorySchema(id=str(doc.id), name=doc.name, description=doc.description)


@router.get("/", response_model=list[CategorySchema])
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    categories = await Category.find_all().skip(skip).limit(limit).to_list()
    return [_category_schema(c) for c in categories]


@router.get("/{category_id}", response_model=CategorySchema)
async def get_category(category_id: str):
    oid = parse_object_id(category_id)
    category = await Category.get(oid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return _category_schema(category)


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category_in: CategoryCreate):
    existing = await Category.find_one(Category.name == category_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists",
        )
    category = Category(name=category_in.name, description=category_in.description)
    await category.insert()
    return _category_schema(category)


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(category_id: str, category_up: CategoryUpdate):
    oid = parse_object_id(category_id)
    category = await Category.get(oid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if category_up.name is not None and category_up.name != category.name:
        existing = await Category.find_one(Category.name == category_up.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another category with this name already exists",
            )
        category.name = category_up.name

    if category_up.description is not None:
        category.description = category_up.description

    await category.save()
    return _category_schema(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str):
    oid = parse_object_id(category_id)
    category = await Category.get(oid)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    linked = await Book.find(Book.category_id == oid).count()
    if linked > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with related books",
        )

    await category.delete()
