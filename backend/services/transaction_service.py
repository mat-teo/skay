from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session, select, func
from models import User, Account, Transaction

def process_transaction(transaction: Transaction, db: Session) -> Transaction:
    """
    Core business logic for checking constraints, ownership, 
    and updating account balances safely.
    """
    # SQLite fix for datetime objects
    if isinstance(transaction.date, str):
        try:
            transaction.date = datetime.fromisoformat(transaction.date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format.")
    elif transaction.date is None:
        transaction.date = datetime.utcnow()

    # 1. Verify User existence
    user = db.get(User, transaction.user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {transaction.user_id} not found.")

    # 2. Handle specific transaction types
    if transaction.type == "expense":
        if not transaction.account_source_id:
            raise HTTPException(status_code=400, detail="Expense requires account_source_id")
        account = db.get(Account, transaction.account_source_id)
        if not account or account.user_id != transaction.user_id:
            raise HTTPException(status_code=403, detail="Invalid or unauthorized account.")
        
        account.balance -= transaction.amount
        db.add(account)

    elif transaction.type == "income":
        if not transaction.account_destination_id:
            raise HTTPException(status_code=400, detail="Income requires account_destination_id")
        account = db.get(Account, transaction.account_destination_id)
        if not account or account.user_id != transaction.user_id:
            raise HTTPException(status_code=403, detail="Invalid or unauthorized account.")
        
        account.balance += transaction.amount
        db.add(account)

    elif transaction.type == "transfer":
        if not transaction.account_source_id or not transaction.account_destination_id:
            raise HTTPException(status_code=400, detail="Transfer requires both source and destination accounts.")
        
        source_acc = db.get(Account, transaction.account_source_id)
        dest_acc = db.get(Account, transaction.account_destination_id)
        
        if not source_acc or not dest_acc:
            raise HTTPException(status_code=404, detail="One or both accounts not found.")
        if source_acc.user_id != transaction.user_id or dest_acc.user_id != transaction.user_id:
            raise HTTPException(status_code=403, detail="Unauthorized account access for this transfer.")
        
        source_acc.balance -= transaction.amount
        dest_acc.balance += transaction.amount
        db.add(source_acc)
        db.add(dest_acc)
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type.")

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction