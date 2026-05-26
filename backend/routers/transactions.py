from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_db
from models import Transaction
from services import finance  # Importiamo il servizio logico

router = APIRouter(tags=["Transactions"])

@router.post("/transactions", response_model=Transaction)
def create_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    # Delegiamo tutta la logica complessa al servizio dedicato
    return finance.process_transaction(transaction, db)

@router.get("/transactions", response_model=List[Transaction])
def get_all_transactions(db: Session = Depends(get_db)):
    return db.exec(select(Transaction)).all()