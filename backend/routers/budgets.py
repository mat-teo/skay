from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from datetime import datetime
from typing import List, Optional
from database import get_db
from models import Budget, BudgetCreate, User, Transaction, TransactionCategory
from auth import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.get("/", response_model=List[Budget])
def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all budgets for the authenticated user."""
    statement = select(Budget).where(Budget.user_id == current_user.id)
    budgets = db.exec(statement).all()
    return budgets

@router.post("/", response_model=Budget)
def create_budget(
    budget: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget."""
    
  
    if budget.amount <= 0:
        raise HTTPException(status_code=400, detail="Budget amount must be positive")
    
    
    if budget.start_date.tzinfo is not None:
        start_date = budget.start_date.replace(tzinfo=None)
    else:
        start_date = budget.start_date
    
    end_date = None
    if budget.end_date:
        if budget.end_date.tzinfo is not None:
            end_date = budget.end_date.replace(tzinfo=None)
        else:
            end_date = budget.end_date
    
    db_budget = Budget(
        user_id=current_user.id,
        name=budget.name,
        category_id=budget.category_id,
        amount=budget.amount,
        period=budget.period,
        start_date=start_date,
        end_date=end_date,
        is_active=budget.is_active
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.put("/{budget_id}", response_model=Budget)
def update_budget(
    budget_id: int,
    budget_update: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing budget."""
    budget = db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    if budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for key, value in budget_update.dict().items():
        setattr(budget, key, value)
    budget.updated_at = datetime.utcnow()
    
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a budget."""
    budget = db.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    if budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(budget)
    db.commit()
    return {"message": "Budget deleted successfully"}

@router.get("/progress")
def get_budget_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate current spending vs budget for active budgets."""
    budgets = db.exec(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.is_active == True
        )
    ).all()
    
    # Get categories for mapping
    categories = db.exec(
        select(TransactionCategory).where(TransactionCategory.user_id == current_user.id)
    ).all()
    category_map = {c.id: c.name for c in categories}
    
    # Get current period dates
    now = datetime.now()
    current_period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get expenses for current period
    expenses = db.exec(
        select(Transaction).where(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense",
            Transaction.date >= current_period_start
        )
    ).all()
    
    # Calculate spent per category
    spent_by_category = {}
    for tx in expenses:
        spent_by_category[tx.category_id] = spent_by_category.get(tx.category_id, 0) + tx.amount
    total_spent = sum(spent_by_category.values())
    
    result = []
    for budget in budgets:
        if budget.category_id:
            spent = spent_by_category.get(budget.category_id, 0)
            category_name = category_map.get(budget.category_id)
        else:
            spent = total_spent
            category_name = None
        
        percentage = (spent / budget.amount) * 100 if budget.amount > 0 else 0
        
        result.append({
            "id": budget.id,
            "name": budget.name,
            "category_id": budget.category_id,
            "category_name": category_name,
            "amount": budget.amount,
            "spent": spent,
            "remaining": budget.amount - spent,
            "percentage": round(percentage, 1),
            "period": budget.period,
            "is_exceeded": spent > budget.amount
        })
    
    return result