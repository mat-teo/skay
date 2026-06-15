from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_db
from models import User
from auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "base_currency": current_user.base_currency,
        "is_verified": current_user.is_verified,
        "created_at": None
    }

@router.put("/me/currency")
def update_user_currency(
    currency_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.base_currency = currency_data.get("base_currency", "EUR")
    db.add(current_user)
    db.commit()
    return {"message": "Currency updated"}