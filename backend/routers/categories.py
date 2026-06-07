from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_db
from models import TransactionCategory, TransactionCategoryCreate, User, Transaction
from auth import get_current_user

router = APIRouter(tags=["Categories"])


@router.post("/categories", response_model=TransactionCategory)
def create_category(
    category_input: TransactionCategoryCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Create a new transaction category (expense or income)."""
    
    # Check if category with same name already exists for this user
    existing = db.exec(
        select(TransactionCategory).where(
            TransactionCategory.user_id == current_user.id,
            TransactionCategory.name == category_input.name
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
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
def get_categories(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get all transaction categories for the authenticated user."""
    statement = select(TransactionCategory).where(TransactionCategory.user_id == current_user.id)
    categories = db.exec(statement).all()
    return categories


@router.put("/categories/{category_id}", response_model=TransactionCategory)
def update_category(
    category_id: int,
    category_input: TransactionCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing category."""
    
    # Get the category
    category = db.get(TransactionCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check ownership
    if category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if new name already exists (excluding current category)
    existing = db.exec(
        select(TransactionCategory).where(
            TransactionCategory.user_id == current_user.id,
            TransactionCategory.name == category_input.name,
            TransactionCategory.id != category_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    # Update fields
    category.name = category_input.name
    category.type = category_input.type
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a category. Transactions using this category will become uncategorized."""
    
    # Get the category
    category = db.get(TransactionCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check ownership
    if category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if category has transactions
    transactions = db.exec(
        select(Transaction).where(Transaction.category_id == category_id)
    ).all()
    
    # Set category_id to NULL for all transactions using this category
    for tx in transactions:
        tx.category_id = None
        db.add(tx)
    
    # Delete the category
    db.delete(category)
    db.commit()
    
    return {
        "message": f"Category '{category.name}' deleted successfully",
        "transactions_updated": len(transactions)
    }