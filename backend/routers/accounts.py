from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_db
from models import Account, User, AccountCreate
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