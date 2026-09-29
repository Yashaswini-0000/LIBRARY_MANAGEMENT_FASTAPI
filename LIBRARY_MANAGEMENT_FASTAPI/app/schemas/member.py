from datetime import date
from pydantic import BaseModel, EmailStr, Field, field_validator


class MemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    address: str = Field(..., min_length=1, max_length=255)
    membership_date: date
    is_active: bool = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        digits = value.replace("+", "").replace("-", "").replace(" ", "")
        if not digits.isdigit() or len(digits) < 10 or len(digits) > 15:
            raise ValueError("Invalid phone number")
        return value


class MemberCreate(MemberBase):
    pass


class MemberUpdate(MemberBase):
    pass


class MemberResponse(MemberBase):
    member_id: int

    class Config:
        from_attributes = True
