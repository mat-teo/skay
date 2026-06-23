from sqlmodel import Session, select
from datetime import datetime
from typing import List, Dict, Any
from models import FinancialGoal, Transaction, Account

def calculate_goal_progress(goal: FinancialGoal, db: Session) -> float:
    """Calculate current amount for a goal based on its tracking mode, bypassing archived items."""
    # If the goal is archived, freeze its progress state and skip intensive DB calculations
    if goal.is_archived:
        return goal.current_amount
        
    if goal.tracking_mode == "category":
        return calculate_from_category(goal, db)
    elif goal.tracking_mode == "account":
        return calculate_from_account(goal, db)
    return 0.0

def calculate_from_category(goal: FinancialGoal, db: Session) -> float:
    """Calculate progress from category transactions, dynamically supporting both income and expenses."""
    if not goal.category_id:
        return 0.0
    
    transactions = db.exec(
        select(Transaction).where(
            Transaction.user_id == goal.user_id,
            Transaction.category_id == goal.category_id
        )
    ).all()
    
    if not transactions:
        return 0.0
    
    total_income = sum(tx.amount for tx in transactions if tx.type == "income")
    total_expense = sum(tx.amount for tx in transactions if tx.type == "expense")
    
    if total_income >= total_expense:
        return float(total_income - total_expense)
    else:
        return float(total_expense - total_income)

def calculate_from_account(goal: FinancialGoal, db: Session) -> float:
    """Calculate progress from account balance using proportional allocation scoped by active goals only."""
    if not goal.account_id or goal.allocation_percentage is None:
        return 0.0
    
    account = db.get(Account, goal.account_id)
    if not account:
        return 0.0
    
    # EXCLUDE archived goals from the total allocation denominator so they don't drain active goals' balances
    all_goals_for_account = db.exec(
        select(FinancialGoal).where(
            FinancialGoal.user_id == goal.user_id,
            FinancialGoal.tracking_mode == "account",
            FinancialGoal.account_id == goal.account_id,
            FinancialGoal.is_archived == False
        )
    ).all()
    
    total_allocation = sum(g.allocation_percentage or 0 for g in all_goals_for_account)
    
    if total_allocation == 0:
        return 0.0
    
    return float((account.balance * goal.allocation_percentage) / total_allocation)

def calculate_goals_summary(goals: List[FinancialGoal], db: Session) -> Dict[str, Any]:
    """Calculate aggregate summary statistics only for non-archived, active goals."""
    active_goals = [g for g in goals if not g.is_archived]
    
    total_target = 0.0
    total_current = 0.0
    
    for goal in active_goals:
        goal.current_amount = calculate_goal_progress(goal, db)
        total_target += goal.target_amount
        total_current += goal.current_amount
    
    return {
        "total_target": total_target,
        "total_current": total_current,
        "total_progress": round((total_current / total_target * 100), 1) if total_target > 0 else 0.0,
        "active_goals": len(active_goals)
    }

def get_goal_status(goal: FinancialGoal, db: Session) -> Dict[str, Any]:
    """Get detailed status metrics for a single goal with safety limits."""
    goal.current_amount = calculate_goal_progress(goal, db)
    
    remaining = max(0.0, goal.target_amount - goal.current_amount)
    
    today = datetime.now().date()
    target_date = goal.target_date.date() if isinstance(goal.target_date, datetime) else goal.target_date
    days_remaining = (target_date - today).days
    
    monthly_savings_needed = 0.0
    if days_remaining > 0 and remaining > 0 and not goal.is_archived:
        monthly_savings_needed = remaining / (days_remaining / 30.4368) 
    
    progress_percent = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0.0
    
    return {
        "id": goal.id,
        "name": goal.name,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "remaining": remaining,
        "progress_percent": min(100.0, max(0.0, round(progress_percent, 1))),
        "days_remaining": max(0, days_remaining),
        "monthly_savings_needed": round(monthly_savings_needed, 2),
        "target_date": goal.target_date,
        "tracking_mode": goal.tracking_mode,
        "category_id": goal.category_id,
        "account_id": goal.account_id,
        "allocation_percentage": goal.allocation_percentage,
        "is_archived": goal.is_archived,
        "icon": goal.icon,
        "color": goal.color
    }