from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from database import get_db
from models import Transaction, TransactionCreate, User
from services import stats_service as stats, transaction_service as finance
from auth import get_current_user

router = APIRouter(tags=["Transactions"])

@router.post("/transactions", response_model=Transaction)
def create_transaction(transaction_input: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_transaction = Transaction(
        user_id=current_user.id,
        amount=transaction_input.amount,
        type=transaction_input.type,
        category_id=transaction_input.category_id,
        date=transaction_input.date or datetime.now(),
        notes=transaction_input.notes,
        account_source_id=transaction_input.account_source_id,
        account_destination_id=transaction_input.account_destination_id
    )
    return finance.process_transaction(db_transaction, db)

@router.get("/transactions", response_model=list[Transaction])
def get_all_transactions(
    current_user: User = Depends(get_current_user),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns transaction history, optionally filtered by date range."""
    stmt = select(Transaction).where(Transaction.user_id == current_user.id)
    if start_date:
        stmt = stmt.where(Transaction.date >= start_date)
    if end_date:
        stmt = stmt.where(Transaction.date <= end_date)
        
    # Order by newest transaction first
    stmt = stmt.order_by(Transaction.date.desc())
    return db.exec(stmt).all()

@router.get("/transactions/stats", tags=["Transactions"])
def get_transaction_stats(
    current_user: User = Depends(get_current_user),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get aggregated financial stats filtered by date range."""
    return stats.get_financial_stats(db, current_user.id, start_date, end_date)