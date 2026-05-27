from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_db
from models import TransactionCategory, TransactionCategoryCreate, User

router = APIRouter(tags=["Categories"])

@router.post("/categories", response_model=TransactionCategory)
def create_category(category_input: TransactionCategoryCreate, db: Session = Depends(get_db)):
    """Create a new transaction category (expense or income)."""
    # Optional check: if a user_id is provided, make sure that user actually exists
    if category_input.user_id:
        if not db.get(User, category_input.user_id):
            raise HTTPException(status_code=404, detail="User specified for this category does not exist.")
            
    db_category = TransactionCategory.from_orm(category_input)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[TransactionCategory])
def get_categories(db: Session = Depends(get_db)):
    """Get all available transaction categories."""
    return db.exec(select(TransactionCategory)).all()