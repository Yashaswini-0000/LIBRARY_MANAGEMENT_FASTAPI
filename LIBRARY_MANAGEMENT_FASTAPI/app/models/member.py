from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Member(Base):
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(15), nullable=False)
    address = Column(String(255), nullable=False)
    membership_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    borrow_records = relationship("Borrow", back_populates="member")
