from datetime import datetime
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address 
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session, select
from database import get_db
from models import Transaction, TransactionCreate, User, TransactionCategory
from services import stats_service as stats, transaction_service as finance
from auth import get_current_user

router = APIRouter(tags=["Transactions"])

limiter = Limiter(key_func=get_remote_address)

@router.post("/transactions", response_model=Transaction)
@limiter.limit("30/minute")
def create_transaction(request: Request, transaction_input: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

@router.get("/transactions/net-worth", tags=["Transactions"])
def get_net_worth_history(
    current_user: User = Depends(get_current_user),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    interval: str = "month",
    db: Session = Depends(get_db)
):
    """
    Get net worth history over time.
    Returns data points for chart (daily, weekly, or monthly aggregated).
    """
    return stats.get_net_worth_history(db, current_user.id, start_date, end_date, interval)

@router.put("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(
    transaction_id: int,
    transaction_input: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing transaction."""
    
    # Get the transaction
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check ownership
    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
     # Check if type changed and call edit_transaction
    new_data = transaction_input.dict()
    
    if transaction.type != new_data.get("type"):
        # Type changed - need full balance adjustment
        finance.edit_transaction(transaction, new_data, db)
    # Update fields
    for key, value in transaction_input.dict().items():
        setattr(transaction, key, value)
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/transactions/{transaction_id}")
@limiter.limit("30/minute")
def delete_transaction(
    request: Request,
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an existing transaction."""
    
    # Get the transaction
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Check ownership
    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return finance.delete_transaction(transaction=transaction,db=db)

@router.get("/transactions/compare", tags=["Transactions"])
def compare_periods(
    period1_start: str = Query(..., description="Start date for period 1 (YYYY-MM-DD)"),
    period1_end: str = Query(..., description="End date for period 1 (YYYY-MM-DD)"),
    period2_start: str = Query(..., description="Start date for period 2 (YYYY-MM-DD)"),
    period2_end: str = Query(..., description="End date for period 2 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare two time periods.
    Returns income, expense, and cashflow for both periods with percentage changes.
    """
    
    # Convert string dates to datetime
    p1_start = datetime.fromisoformat(period1_start)
    p1_end = datetime.fromisoformat(period1_end)
    p2_start = datetime.fromisoformat(period2_start)
    p2_end = datetime.fromisoformat(period2_end)
    
    # Get stats for period 1
    stats1 = stats.get_financial_stats(db, current_user.id, p1_start, p1_end)
    
    # Get stats for period 2
    stats2 = stats.get_financial_stats(db, current_user.id, p2_start, p2_end)
    
    # Calculate percentage changes
    def calc_change(old, new):
        if old == 0:
            return 100 if new > 0 else 0
        return round(((new - old) / old) * 100, 1)
    
    income_change = calc_change(stats1["total_income"], stats2["total_income"])
    expense_change = calc_change(stats1["total_expense"], stats2["total_expense"])
    
    cashflow1 = stats1["net_savings"]
    cashflow2 = stats2["net_savings"]
    cashflow_change = calc_change(cashflow1, cashflow2)
    
    return {
        "period1": {
            "start_date": period1_start,
            "end_date": period1_end,
            "income": stats1["total_income"],
            "expense": stats1["total_expense"],
            "cashflow": cashflow1
        },
        "period2": {
            "start_date": period2_start,
            "end_date": period2_end,
            "income": stats2["total_income"],
            "expense": stats2["total_expense"],
            "cashflow": cashflow2
        },
        "comparison": {
            "income_change": income_change,
            "expense_change": expense_change,
            "cashflow_change": cashflow_change
        }
    }

@router.get("/transactions/export")
def export_transactions(
    current_user: User = Depends(get_current_user),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Export transactions as CSV."""
    
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    
    transactions = db.exec(query.order_by(Transaction.date.desc())).all()
    
    # Get categories mapping
    categories = db.exec(select(TransactionCategory)).all()
    cat_map = {c.id: c.name for c in categories}
    
    # Build CSV content
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Category', 'Amount (€)', 'Notes', 'Source Account', 'Destination Account'])
    
    for tx in transactions:
        writer.writerow([
            tx.date.strftime('%Y-%m-%d'),
            tx.type,
            cat_map.get(tx.category_id, 'Uncategorized'),
            tx.amount,
            tx.notes or '',
            tx.account_source_id or '',
            tx.account_destination_id or ''
        ])
    
    # Return as downloadable file
    from fastapi.responses import Response
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.csv"}
    )