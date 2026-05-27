from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session, select, func
from models import User, Account, Transaction


def get_financial_stats(db: Session, user_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """
    Calculate filtered total income and expenses for a user within a specific timeframe.
    """
    # Base statement for expense
    expense_stmt = select(func.sum(Transaction.amount)).where(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    )
    
    # Base statement for income
    income_stmt = select(func.sum(Transaction.amount)).where(
        Transaction.user_id == user_id,
        Transaction.type == "income"
    )

    # Apply date filters if provided
    if start_date:
        expense_stmt = expense_stmt.where(Transaction.date >= start_date)
        income_stmt = income_stmt.where(Transaction.date >= start_date)
    if end_date:
        expense_stmt = expense_stmt.where(Transaction.date <= end_date)
        income_stmt = income_stmt.where(Transaction.date <= end_date)

    total_expense = db.exec(expense_stmt).one() or 0.0
    total_income = db.exec(income_stmt).one() or 0.0
    net_savings = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_savings": net_savings
    }