from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_db
from models import Account, User

router = APIRouter(tags=["Accounts"])

@router.get("/accounts", response_model=List[Account])
def get_all_accounts(db: Session = Depends(get_db)):
    return db.exec(select(Account)).all()

@router.post("/accounts", response_model=Account)
def create_account(account: Account, db: Session = Depends(get_db)):
    if not db.get(User, account.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    db.add(account)
    db.commit()
    db.refresh(account)
    return account