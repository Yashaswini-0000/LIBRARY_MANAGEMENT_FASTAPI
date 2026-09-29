from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.member import Member
from app.schemas.member import MemberCreate, MemberResponse, MemberUpdate

router = APIRouter(prefix="/members", tags=["Members"])


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(data: MemberCreate, db: Session = Depends(get_db)):
    if db.query(Member).filter(Member.email == str(data.email)).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    member = Member(**data.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("", response_model=list[MemberResponse])
def get_members(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="Invalid pagination values")
    return db.query(Member).offset(skip).limit(limit).all()


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.member_id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, data: MemberUpdate, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.member_id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    duplicate = (
        db.query(Member)
        .filter(Member.email == str(data.email), Member.member_id != member_id)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Email already exists")

    for key, value in data.model_dump().items():
        setattr(member, key, value)

    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.member_id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    active_borrows = sum(1 for b in member.borrow_records if b.return_date is None)
    if active_borrows:
        raise HTTPException(status_code=400, detail="Member has active borrowed books")

    db.delete(member)
    db.commit()
    return {"message": "Member deleted successfully"}
