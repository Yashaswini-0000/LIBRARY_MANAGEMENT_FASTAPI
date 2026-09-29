from pydantic import BaseModel, Field, field_validator


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=150)
    isbn: str = Field(..., min_length=10, max_length=20)
    category_id: int = Field(..., gt=0)
    total_copies: int = Field(..., ge=1)
    available_copies: int = Field(..., ge=0)
    published_year: int = Field(..., ge=1000, le=2100)

    @field_validator("available_copies")
    @classmethod
    def validate_available(cls, value, info):
        total = info.data.get("total_copies")
        if total is not None and value > total:
            raise ValueError("available_copies cannot exceed total_copies")
        return value


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookResponse(BookBase):
    book_id: int

    class Config:
        from_attributes = True
