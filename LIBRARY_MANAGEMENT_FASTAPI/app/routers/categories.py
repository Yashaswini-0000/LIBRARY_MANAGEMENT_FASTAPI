from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.category_name == data.category_name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Category name already exists")

    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("", response_model=list[CategoryResponse])
def get_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="Invalid pagination values")
    return db.query(Category).offset(skip).limit(limit).all()


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    duplicate = (
        db.query(Category)
        .filter(Category.category_name == data.category_name, Category.category_id != category_id)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Category name already exists")

    for key, value in data.model_dump().items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.books:
        raise HTTPException(status_code=400, detail="Cannot delete category while books exist")

    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}
