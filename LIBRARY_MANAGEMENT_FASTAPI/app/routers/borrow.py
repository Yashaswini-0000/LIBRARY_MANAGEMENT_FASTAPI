from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.book import Book
from app.models.member import Member
from app.models.borrow import Borrow
from app.schemas.borrow import BorrowCreate, BorrowResponse

router = APIRouter(tags=["Borrow & Return"])


@router.post("/borrow", response_model=BorrowResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(data: BorrowCreate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    member = db.query(Member).filter(Member.member_id == data.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not member.is_active:
        raise HTTPException(status_code=400, detail="Inactive members cannot borrow books")

    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No copies available")

    active_count = db.query(Borrow).filter(
        Borrow.member_id == data.member_id,
        Borrow.return_date.is_(None)
    ).count()

    if active_count >= 3:
        raise HTTPException(status_code=400, detail="A member cannot borrow more than 3 books at a time")

    duplicate = db.query(Borrow).filter(
        Borrow.member_id == data.member_id,
        Borrow.book_id == data.book_id,
        Borrow.return_date.is_(None)
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=400,
            detail="Member already has this book and must return it first"
        )

    today = date.today()
    borrow = Borrow(
        book_id=data.book_id,
        member_id=data.member_id,
        borrow_date=today,
        due_date=today + timedelta(days=14),
        status="Borrowed"
    )

    book.available_copies -= 1
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow


@router.put("/return/{borrow_id}", response_model=BorrowResponse)
def return_book(borrow_id: int, db: Session = Depends(get_db)):
    borrow = db.query(Borrow).filter(Borrow.borrow_id == borrow_id).first()
    if not borrow:
        raise HTTPException(status_code=404, detail="Borrow record not found")

    if borrow.return_date is not None:
        raise HTTPException(status_code=400, detail="Book has already been returned")

    today = date.today()
    borrow.return_date = today
    borrow.status = "Overdue" if today > borrow.due_date else "Returned"

    book = db.query(Book).filter(Book.book_id == borrow.book_id).first()
    if book:
        book.available_copies += 1
        if book.available_copies > book.total_copies:
            book.available_copies = book.total_copies

    db.commit()
    db.refresh(borrow)
    return borrow


@router.get("/members/{member_id}/books", response_model=list[BorrowResponse])
def member_books(member_id: int, db: Session = Depends(get_db)):
    if not db.query(Member).filter(Member.member_id == member_id).first():
        raise HTTPException(status_code=404, detail="Member not found")

    return db.query(Borrow).filter(
        Borrow.member_id == member_id,
        Borrow.return_date.is_(None)
    ).all()


@router.get("/books/{book_id}/borrow-history", response_model=list[BorrowResponse])
def book_history(book_id: int, db: Session = Depends(get_db)):
    if not db.query(Book).filter(Book.book_id == book_id).first():
        raise HTTPException(status_code=404, detail="Book not found")

    return db.query(Borrow).filter(Borrow.book_id == book_id).all()


@router.get("/borrow/overdue", response_model=list[BorrowResponse])
def overdue_books(db: Session = Depends(get_db)):
    today = date.today()
    records = db.query(Borrow).filter(
        Borrow.return_date.is_(None),
        Borrow.due_date < today
    ).all()

    for record in records:
        record.status = "Overdue"

    if records:
        db.commit()

    return records
