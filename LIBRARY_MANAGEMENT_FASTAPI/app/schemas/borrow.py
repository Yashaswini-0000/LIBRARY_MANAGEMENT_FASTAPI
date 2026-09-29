from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class BorrowCreate(BaseModel):
    book_id: int = Field(..., gt=0)
    member_id: int = Field(..., gt=0)


class BorrowResponse(BaseModel):
    borrow_id: int
    book_id: int
    member_id: int
    borrow_date: date
    due_date: date
    return_date: Optional[date] = None
    status: str

    class Config:
        from_attributes = True
