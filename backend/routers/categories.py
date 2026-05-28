from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_db
from models import TransactionCategory, TransactionCategoryCreate, User
from auth import get_current_user

router = APIRouter(tags=["Categories"])

@router.post("/categories", response_model=TransactionCategory)
def create_category(
    category_input: TransactionCategoryCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Create a new transaction category (expense or income)."""
    
    db_category = TransactionCategory(
        user_id=current_user.id,
        name=category_input.name,
        type=category_input.type
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[TransactionCategory])
def get_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all available transaction categories."""
    statement = select(TransactionCategory).where(TransactionCategory.user_id == current_user.id)
    categories = db.exec(statement).all()
    return categories