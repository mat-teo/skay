from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from datetime import datetime
from typing import List, Optional
from database import get_db
from models import RecurringTransaction, Account, TransactionCategory, Transaction, User
from auth import get_current_user
from services.recurring_service import calculate_next_date, advance_next_date

router = APIRouter(prefix="/recurring", tags=["Recurring"])

@router.get("/", response_model=List[RecurringTransaction])
def get_recurring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active recurring transactions for the authenticated user."""
    statement = select(RecurringTransaction).where(
        RecurringTransaction.user_id == current_user.id,
        RecurringTransaction.is_active == True
    )
    return db.exec(statement).all()

@router.post("/", response_model=RecurringTransaction)
def create_recurring(
    recurring: RecurringTransaction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recurring transaction."""
    
    # Convert start_date from string to datetime if needed
    if isinstance(recurring.start_date, str):
        recurring.start_date = datetime.fromisoformat(recurring.start_date.replace('Z', '+00:00'))
    if recurring.end_date and isinstance(recurring.end_date, str):
        recurring.end_date = datetime.fromisoformat(recurring.end_date.replace('Z', '+00:00'))
    
    # Validation
    if recurring.amount < 0.01:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0.01")
    
    if not recurring.category_id:
        raise HTTPException(status_code=400, detail="Category is required")
    
    if not recurring.account_id:
        raise HTTPException(status_code=400, detail="Account is required")
    
    # Verify category
    category = db.get(TransactionCategory, recurring.category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Verify account
    account = db.get(Account, recurring.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Invalid account")
    
    # Calculate next date
    recurring.next_date = calculate_next_date(recurring)
    recurring.user_id = current_user.id
    
    db.add(recurring)
    db.commit()
    db.refresh(recurring)
    return recurring

@router.put("/{recurring_id}", response_model=RecurringTransaction)
def update_recurring(
    recurring_id: int,
    recurring_update: RecurringTransaction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a recurring transaction."""
    recurring = db.get(RecurringTransaction, recurring_id)
    if not recurring:
        raise HTTPException(status_code=404, detail="Not found")
    if recurring.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Validation
    if recurring_update.amount < 0.01:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0.01")
    
    if not recurring_update.category_id:
        raise HTTPException(status_code=400, detail="Category is required")
    
    if not recurring_update.account_id:
        raise HTTPException(status_code=400, detail="Account is required")
    
    category = db.get(TransactionCategory, recurring_update.category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    account = db.get(Account, recurring_update.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Invalid account")
    
    # Update fields
    for key, value in recurring_update.dict().items():
        if key not in ['id','user_id','created_at']:
            setattr(recurring, key, value)
    
    # Recalculate next_date if start_date changed
    if recurring_update.start_date != recurring.start_date:
        recurring.next_date = calculate_next_date(recurring)
    
    recurring.updated_at = datetime.utcnow()
    db.add(recurring)
    db.commit()
    db.refresh(recurring)
    return recurring

@router.delete("/{recurring_id}")
def delete_recurring(
    recurring_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a recurring transaction."""
    recurring = db.get(RecurringTransaction, recurring_id)
    if not recurring:
        raise HTTPException(status_code=404, detail="Not found")
    if recurring.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    recurring.is_active = False
    db.add(recurring)
    db.commit()
    return {"message": "Deleted"}

@router.get("/upcoming")
def get_upcoming(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Number of upcoming occurrences")
):
    """Get upcoming occurrences for all active recurring transactions."""
    recurrings = db.exec(
        select(RecurringTransaction).where(
            RecurringTransaction.user_id == current_user.id,
            RecurringTransaction.is_active == True
        )
    ).all()
    
    results = []
    for rec in recurrings:
        results.append({
            "id": rec.id,
            "name": rec.name,
            "amount": rec.amount,
            "type": rec.type,
            "next_date": rec.next_date.isoformat(),
            "category_id": rec.category_id,
            "frequency": rec.frequency
        })
    
    # Sort by next_date and limit
    results.sort(key=lambda x: x["next_date"])
    return results[:limit]

@router.post("/{recurring_id}/pay")
def pay_recurring(
    recurring_id: int,
    amount: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a transaction from a recurring transaction and advance next_date."""
    recurring = db.get(RecurringTransaction, recurring_id)
    if not recurring:
        raise HTTPException(status_code=404, detail="Not found")
    if recurring.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Ensure next_date is datetime
    if isinstance(recurring.next_date, str):
        recurring.next_date = datetime.fromisoformat(recurring.next_date.replace('Z', '+00:00'))
    
    pay_amount = amount or recurring.amount
    
    # Get the account
    account = db.get(Account, recurring.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Update account balance based on transaction type
    if recurring.type == "expense":
        account.balance -= pay_amount
    elif recurring.type == "income":
        account.balance += pay_amount
    
    db.add(account)
    
    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        amount=pay_amount,
        type=recurring.type,
        category_id=recurring.category_id,
        account_source_id=recurring.account_id if recurring.type == "expense" else None,
        account_destination_id=recurring.account_id if recurring.type == "income" else None,
        date=datetime.now(),
        notes=f"{recurring.name} - {datetime.now().strftime('%B %Y')}",
        recurring_id=recurring.id
    )
    db.add(transaction)
    
    # Advance next_date to next period
    recurring.next_date = advance_next_date(recurring)
    db.add(recurring)
    
    db.commit()
    db.refresh(transaction)
    
    return transaction

@router.post("/{recurring_id}/skip")
def skip_recurring(
    recurring_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Skip the next occurrence of a recurring transaction."""
    recurring = db.get(RecurringTransaction, recurring_id)
    if not recurring:
        raise HTTPException(status_code=404, detail="Not found")
    if recurring.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Ensure next_date is datetime
    if isinstance(recurring.next_date, str):
        recurring.next_date = datetime.fromisoformat(recurring.next_date.replace('Z', '+00:00'))
    
    # Create skip transaction (amount = 0)
    transaction = Transaction(
        user_id=current_user.id,
        amount=0,
        type=recurring.type,
        category_id=recurring.category_id,
        date=datetime.now(),
        notes=f"[SKIPPED] {recurring.name} - {datetime.now().strftime('%B %Y')}",
        recurring_id=recurring.id
    )
    db.add(transaction)
    
    # Advance next_date to next period
    recurring.next_date = advance_next_date(recurring)
    db.add(recurring)
    
    db.commit()
    db.refresh(transaction)
    
    return {"message": "Skipped"}