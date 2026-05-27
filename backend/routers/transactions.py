from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from database import get_db
from models import Transaction, TransactionCreate
from services import finance

router = APIRouter(tags=["Transactions"])

@router.post("/transactions", response_model=Transaction)
def create_transaction(transaction_input: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction.from_orm(transaction_input)
    return finance.process_transaction(db_transaction, db)

@router.get("/transactions", response_model=list[Transaction])
def get_all_transactions(
    user_id: int = Query(1),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns transaction history, optionally filtered by date range."""
    stmt = select(Transaction).where(Transaction.user_id == user_id)
    if start_date:
        stmt = stmt.where(Transaction.date >= start_date)
    if end_date:
        stmt = stmt.where(Transaction.date <= end_date)
        
    # Order by newest transaction first
    stmt = stmt.order_by(Transaction.date.desc())
    return db.exec(stmt).all()

@router.get("/transactions/stats", tags=["Transactions"])
def get_transaction_stats(
    user_id: int = Query(1),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get aggregated financial stats filtered by date range."""
    return finance.get_financial_stats(db, user_id, start_date, end_date)