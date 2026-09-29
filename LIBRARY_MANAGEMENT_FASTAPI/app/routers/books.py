from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.book import Book
from app.models.category import Category
from app.models.borrow import Borrow
from app.schemas.book import BookCreate, BookResponse, BookUpdate

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    if not db.query(Category).filter(Category.category_id == data.category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")

    if db.query(Book).filter(Book.isbn == data.isbn).first():
        raise HTTPException(status_code=409, detail="ISBN already exists")

    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("", response_model=list[BookResponse])
def get_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="Invalid pagination values")

    query = db.query(Book)

    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if category_id:
        query = query.filter(Book.category_id == category_id)

    return query.offset(skip).limit(limit).all()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not db.query(Category).filter(Category.category_id == data.category_id).first():
        raise HTTPException(status_code=404, detail="Category not found")

    duplicate = (
        db.query(Book)
        .filter(Book.isbn == data.isbn, Book.book_id != book_id)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="ISBN already exists")

    currently_borrowed = db.query(Borrow).filter(
        Borrow.book_id == book_id,
        Borrow.return_date.is_(None)
    ).count()

    borrowed_copies = book.total_copies - book.available_copies
    if data.total_copies < borrowed_copies:
        raise HTTPException(
            status_code=400,
            detail="total_copies cannot be less than currently borrowed copies"
        )

    if data.available_copies > data.total_copies - currently_borrowed:
        raise HTTPException(
            status_code=400,
            detail="available_copies conflicts with active borrow records"
        )

    for key, value in data.model_dump().items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    active_borrows = db.query(Borrow).filter(
        Borrow.book_id == book_id,
        Borrow.return_date.is_(None)
    ).count()

    if active_borrows > 0:
        raise HTTPException(
            status_code=400,
            detail="Books that are currently borrowed cannot be deleted"
        )

    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}
