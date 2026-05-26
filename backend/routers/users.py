from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_db
from models import User

router = APIRouter(tags=["Users"])

@router.post("/users", response_model=User)
def create_user(user: User, db: Session = Depends(get_db)):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user