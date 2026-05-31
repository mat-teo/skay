from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_db
from models import Account, User, AccountCreate, Transaction
from auth import get_current_user

router = APIRouter(tags=["Accounts"])

@router.get("/accounts", response_model=List[Account])
def get_all_accounts(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    accounts = db.exec(select(Account).where(Account.user_id == current_user.id)).all()
    return accounts

@router.post("/accounts", response_model=Account)
def create_account(
    account: AccountCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_account = Account(
        user_id=current_user.id,
        name=account.name,
        type=account.type,
        balance=account.balance
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.put("/accounts/{account_id}", response_model=Account)
def update_account(
    account_id: int,
    account_update: AccountCreate,  # name, type, balance
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing account."""
    
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    account.name = account_update.name
    account.type = account_update.type
    account.balance = account_update.balance
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/accounts/{account_id}")
def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an account and all its transactions."""
    
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find all transactions linked to this account
    transactions = db.exec(
        select(Transaction).where(
            (Transaction.account_source_id == account_id) |
            (Transaction.account_destination_id == account_id)
        )
    ).all()
    
    # Delete all related transactions
    for tx in transactions:
        db.delete(tx)
    
    # Delete the account
    db.delete(account)
    db.commit()
    
    return {
        "message": f"Account '{account.name}' and {len(transactions)} transactions deleted"
    }