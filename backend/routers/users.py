from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from database import get_db
from models import User, UserCreate

router = APIRouter(tags=["Users"])

@router.post("/users", response_model=User)
def create_user(user_input: UserCreate, db: Session = Depends(get_db)):
    # Convert input schema into database table structure
    db_user = User.from_orm(user_input)
    
    # SQLite fix: Ensure optional datetime fields are proper Python datetime objects if populated
    if db_user.otp_expires_at and isinstance(db_user.otp_expires_at, str):
        try:
            db_user.otp_expires_at = datetime.fromisoformat(db_user.otp_expires_at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid otp_expires_at date format.")
            
    if db_user.reset_token_expires_at and isinstance(db_user.reset_token_expires_at, str):
        try:
            db_user.reset_token_expires_at = datetime.fromisoformat(db_user.reset_token_expires_at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid reset_token_expires_at date format.")

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user