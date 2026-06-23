from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from typing import List
from database import get_db
from models import FinancialGoal, FinancialGoalCreate, User, Account, TransactionCategory
from auth import get_current_user
from services.goal_service import (
    calculate_goal_progress, 
    calculate_goals_summary, 
    get_goal_status
)

router = APIRouter(prefix="/goals", tags=["Goals"])

def validate_goal_payload(goal: FinancialGoalCreate, user_id: int, db: Session):
    """Reusable centralized validator to enforce security boundary checks and data consistency."""
    if goal.tracking_mode == "category" and not goal.category_id:
        raise HTTPException(status_code=400, detail="Category ID required for category tracking")
    
    if goal.tracking_mode == "account" and not goal.account_id:
        raise HTTPException(status_code=400, detail="Account ID required for account tracking")
    
    if goal.tracking_mode == "account" and goal.allocation_percentage is None:
        raise HTTPException(status_code=400, detail="Allocation percentage required for account tracking")
    
    if goal.allocation_percentage is not None and (goal.allocation_percentage < 0 or goal.allocation_percentage > 100):
        raise HTTPException(status_code=400, detail="Allocation percentage must be between 0 and 100")
    
    if goal.category_id:
        category = db.get(TransactionCategory, goal.category_id)
        if not category or category.user_id != user_id:
            raise HTTPException(status_code=404, detail="Category not found or unauthorized")
            
    if goal.account_id:
        account = db.get(Account, goal.account_id)
        if not account or account.user_id != user_id:
            raise HTTPException(status_code=404, detail="Account not found or unauthorized")

@router.get("/", response_model=List[FinancialGoal])
def get_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.exec(select(FinancialGoal).where(FinancialGoal.user_id == current_user.id)).all()

@router.get("/summary")
def get_goals_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goals = db.exec(select(FinancialGoal).where(FinancialGoal.user_id == current_user.id)).all()
    return calculate_goals_summary(goals, db)

@router.get("/status")
def get_goals_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goals = db.exec(select(FinancialGoal).where(FinancialGoal.user_id == current_user.id)).all()
    return [get_goal_status(goal, db) for goal in goals]

@router.post("/", response_model=FinancialGoal)
def create_goal(goal: FinancialGoalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    validate_goal_payload(goal, current_user.id, db)
    
    db_goal = FinancialGoal(
        user_id=current_user.id,
        name=goal.name,
        target_amount=goal.target_amount,
        target_date=goal.target_date,
        icon=goal.icon or "🎯",
        color=goal.color or "#4f46e5",
        tracking_mode=goal.tracking_mode,
        category_id=goal.category_id if goal.tracking_mode == "category" else None,
        account_id=goal.account_id if goal.tracking_mode == "account" else None,
        allocation_percentage=goal.allocation_percentage if goal.tracking_mode == "account" else None,
        is_archived=False,
        current_amount=0.0
    )
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    db_goal.current_amount = calculate_goal_progress(db_goal, db)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.put("/{goal_id}", response_model=FinancialGoal)
def update_goal(goal_id: int, goal_update: FinancialGoalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = db.get(FinancialGoal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    validate_goal_payload(goal_update, current_user.id, db)
    
    for key, value in goal_update.dict().items():
        setattr(goal, key, value)
    
    if goal.tracking_mode == "category":
        goal.account_id = None
        goal.allocation_percentage = None
    else:
        goal.category_id = None
        
    goal.updated_at = datetime.utcnow()
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    goal.current_amount = calculate_goal_progress(goal, db)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@router.post("/{goal_id}/archive")
def archive_goal(goal_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """NEW: Explicit endpoint to flip archival and freeze historical baseline progress metrics."""
    goal = db.get(FinancialGoal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    goal.is_archived = True
    goal.updated_at = datetime.utcnow()
    
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return {"message": "Goal successfully achieved and archived", "is_archived": True}

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = db.get(FinancialGoal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully"}