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

def delete_transaction(transaction: Transaction, db: Session):
    """Delete a transaction and revert the account balance."""
    
    if transaction.type == "expense":
        account = db.get(Account, transaction.account_source_id)
        if not account:
            raise HTTPException(status_code=404, detail="Source account not found")
        account.balance += transaction.amount
        db.add(account)
        
    elif transaction.type == "income":
        account = db.get(Account, transaction.account_destination_id)
        if not account:
            raise HTTPException(status_code=404, detail="Destination account not found")
        account.balance -= transaction.amount
        db.add(account)
        
    elif transaction.type == "transfer":
        # For transfers, no balance change
        pass
    
    # Delete the transaction
    db.delete(transaction)
    db.commit()
    
    return {"message": f"{transaction.type.capitalize()} deleted successfully"}

def edit_transaction(
    old_transaction: Transaction, 
    new_transaction_data: dict, 
    db: Session
):
    """
    Edit an existing transaction and adjust account balances accordingly.
    
    Handles cases where type, amount, or accounts change.
    """
    
    # Check if type changed
    type_changed = old_transaction.type != new_transaction_data.get("type")
    
    # Check if amount changed
    amount_changed = old_transaction.amount != new_transaction_data.get("amount")
    
    # Check if accounts changed
    source_changed = old_transaction.account_source_id != new_transaction_data.get("account_source_id")
    dest_changed = old_transaction.account_destination_id != new_transaction_data.get("account_destination_id")
    
    # Case 1: Type changed (expense ↔ income)
    if type_changed:
        # Revert old transaction effect
        if old_transaction.type == "expense":
            # Old expense: remove from source account (add back)
            old_account = db.get(Account, old_transaction.account_source_id)
            if old_account:
                old_account.balance += old_transaction.amount
                db.add(old_account)
        elif old_transaction.type == "income":
            # Old income: remove from destination account (subtract)
            old_account = db.get(Account, old_transaction.account_destination_id)
            if old_account:
                old_account.balance -= old_transaction.amount
                db.add(old_account)
        
        # Apply new transaction effect
        if new_transaction_data.get("type") == "expense":
            new_account = db.get(Account, new_transaction_data.get("account_source_id"))
            if new_account:
                new_account.balance -= new_transaction_data.get("amount", 0)
                db.add(new_account)
        elif new_transaction_data.get("type") == "income":
            new_account = db.get(Account, new_transaction_data.get("account_destination_id"))
            if new_account:
                new_account.balance += new_transaction_data.get("amount", 0)
                db.add(new_account)
    
    # Case 2: Same type, but amount or account changed
    else:
        if old_transaction.type == "expense":
            account = db.get(Account, old_transaction.account_source_id)
            if account:
                # Revert old amount
                account.balance += old_transaction.amount
                
                # Apply new amount (if account changed, use new account)
                if source_changed:
                    account = db.get(Account, new_transaction_data.get("account_source_id"))
                
                account.balance -= new_transaction_data.get("amount", 0)
                db.add(account)
                
        elif old_transaction.type == "income":
            account = db.get(Account, old_transaction.account_destination_id)
            if account:
                # Revert old amount
                account.balance -= old_transaction.amount
                
                # Apply new amount
                if dest_changed:
                    account = db.get(Account, new_transaction_data.get("account_destination_id"))
                
                account.balance += new_transaction_data.get("amount", 0)
                db.add(account)
    
    return {"message": "Transaction updated successfully"}