# backend/routers/import_data.py
import pandas as pd
import io
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request
from sqlmodel import Session, select
from database import get_db
from models import User, Transaction, Account, TransactionCategory
from auth import get_current_user
import services.import_csv
from rate_limit import limiter

router = APIRouter(prefix="/import", tags=["Import"])

def detect_csv_type(df: pd.DataFrame) -> str:
    """
    Detect if the cleaned DataFrame matches a Skay export layout or a bank statement structure.
    Supports international bank formats like Revolut ('money in/out').
    """
    columns = list(df.columns)
    
    # 1. Exact match for Skay native layout standard
    skay_columns = ['date', 'description', 'amount', 'type', 'category', 'account']
    if all(col in columns for col in skay_columns):
        return 'skay'
    
    # 2. Resilient check for standard multi-currency bank statements (Italian or International)
    has_date = any(c in columns for c in ['date', 'data', 'booking date', 'value date'])
    has_amount = any(c in columns for c in ['amount', 'importo', 'money in/out', 'value', 'total'])
    
    if has_date and has_amount:
        return 'bank'
    
    return 'unknown'


@router.post("/csv/preview")
@limiter.limit("10/minute")
async def preview_csv(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Preview uploaded CSV file dynamically skipping metadata headers 
    and returning structure specifications.
    """
    content = await file.read()
    content_str = content.decode('utf-8')
    
    try:
        # Delegate clean parsing and layout filtering to the service package
        df = services.import_csv.clean_and_parse_bank_csv(content_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV file layout: {str(e)}")
        
    csv_type = detect_csv_type(df)
    
    user_accounts = db.exec(
        select(Account).where(Account.user_id == current_user.id)
    ).all()
    
    return {
        "csv_type": csv_type,
        "columns": df.columns.tolist(),
        "preview": df.head(5).to_dict(orient='records'),
        "total_rows": len(df),
        "accounts": [{"id": a.id, "name": a.name} for a in user_accounts],
        "is_skay_format": csv_type == 'skay'
    }


@router.post("/csv/execute")
@limiter.limit("5/minute")
async def execute_import(
    request: Request,
    file: UploadFile = File(...),
    target_account_id: Optional[int] = Query(None),
    auto_create_categories: bool = Query(True),
    auto_create_accounts: bool = Query(True),
    skip_duplicates: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = await file.read()
    content_str = content.decode('utf-8')
    
    try:
        df = services.import_csv.clean_and_parse_bank_csv(content_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract records: {str(e)}")
        
    csv_type = detect_csv_type(df)
    if csv_type == 'unknown':
        raise HTTPException(status_code=400, detail="Unknown CSV format mapping.")
    
    imported = 0
    skipped = 0
    errors = []
    created_categories = []
    created_accounts = []
    account_balance_changes = {}
    
    existing_categories = db.exec(select(TransactionCategory).where(TransactionCategory.user_id == current_user.id)).all()
    cat_map = {c.name.lower(): c for c in existing_categories}
    
    existing_accounts = db.exec(select(Account).where(Account.user_id == current_user.id)).all()
    acc_map = {a.name.lower(): a for a in existing_accounts}
    
    if csv_type == 'skay':
        date_col, desc_col, amount_col, type_col, category_col, account_col = 'date', 'description', 'amount', 'type', 'category', 'account'
    else:
        columns = list(df.columns)
        date_col = next((c for c in ['data', 'date', 'booking date', 'value date'] if c in columns), None)
        desc_col = next((c for c in ['descrizione', 'description', 'narrative', 'reference'] if c in columns), None)
        amount_col = next((c for c in ['importo', 'amount', 'money in/out', 'value', 'total'] if c in columns), None)
        category_col = next((c for c in ['categoria', 'category'] if c in columns), None)
        account_col, type_col = None, None
        
        if not date_col or not amount_col:
            raise HTTPException(status_code=400, detail="Required date or amount mapping targets are missing.")
        if not target_account_id:
            raise HTTPException(status_code=400, detail="Please select a target destination account.")
        
        target_account = db.get(Account, target_account_id)
        if not target_account or target_account.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Selected target destination account not found.")
            
    for idx, row in df.iterrows():
        try:
            date_str = row.get(date_col)
            if not date_str or pd.isna(date_str):
                skipped += 1
                continue
            
            # Clean embedded newline formatting characters from text blocks
            date_str = str(date_str).replace('\n', ' ').strip()
            try:
                date = pd.to_datetime(date_str).to_pydatetime()
            except:
                date = datetime.now()
            
            amount_str = row.get(amount_col)
            if amount_str is None or pd.isna(amount_str):
                skipped += 1
                continue
            
            raw_amount = services.import_csv.parse_amount(amount_str)
            if raw_amount is None:
                skipped += 1
                continue
            
            if csv_type == 'skay':
                type_val = str(row.get(type_col, '')).lower()
                tx_type = 'income' if 'income' in type_val else 'expense'
                amount = abs(raw_amount)
            else:
                tx_type = 'income' if raw_amount > 0 else 'expense'
                amount = abs(raw_amount)
            
            category_name = row.get(category_col) if category_col else None
            category_id = None
            if category_name and not pd.isna(category_name):
                cat_key = str(category_name).replace('\n', ' ').lower().strip()
                if cat_key in cat_map:
                    category_id = cat_map[cat_key].id
                elif auto_create_categories:
                    new_cat = TransactionCategory(
                        user_id=current_user.id,
                        name=str(category_name).replace('\n', ' ').strip().title(),
                        type=tx_type
                    )
                    db.add(new_cat)
                    db.commit()
                    db.refresh(new_cat)
                    category_id = new_cat.id
                    cat_map[cat_key] = new_cat
                    created_categories.append(new_cat.name)
            
            account_id = None
            if csv_type == 'skay' and account_col:
                acc_name = row.get(account_col)
                if acc_name and not pd.isna(acc_name):
                    acc_key = str(acc_name).lower().strip()
                    if acc_key in acc_map:
                        account_id = acc_map[acc_key].id
                    elif auto_create_accounts:
                        new_acc = Account(user_id=current_user.id, name=str(acc_name).strip().title(), type='bank', balance=0.0)
                        db.add(new_acc)
                        db.commit()
                        db.refresh(new_acc)
                        account_id = new_acc.id
                        acc_map[acc_key] = new_acc
                        created_accounts.append(new_acc.name)
            elif csv_type == 'bank':
                account_id = target_account_id
            
            if skip_duplicates and account_id:
                dup_check = db.exec(
                    select(Transaction).where(
                        Transaction.user_id == current_user.id,
                        Transaction.date == date,
                        Transaction.amount == amount,
                        Transaction.type == tx_type,
                        ((Transaction.account_source_id == account_id) if tx_type == 'expense' else (Transaction.account_destination_id == account_id))
                    )
                ).first()
                if dup_check:
                    skipped += 1
                    continue
            
            notes_text = str(row.get(desc_col, '')).replace('\n', ' ').strip() if desc_col else ''
            transaction = Transaction(
                user_id=current_user.id,
                amount=amount,
                type=tx_type,
                category_id=category_id,
                date=date,
                notes=notes_text,
                account_source_id=account_id if tx_type == 'expense' else None,
                account_destination_id=account_id if tx_type == 'income' else None
            )
            
            if account_id:
                if account_id not in account_balance_changes:
                    account_balance_changes[account_id] = 0.0
                account_balance_changes[account_id] += (-amount if tx_type == 'expense' else amount)
            
            db.add(transaction)
            imported += 1
            
        except Exception as e:
            skipped += 1
            errors.append(f"Row {idx + 2}: {str(e)}")
            continue
            
    # Apply balance corrections and commit all operations in a single atomic database batch
    if imported > 0:
        for acc_id, balance_delta in account_balance_changes.items():
            account = db.get(Account, acc_id)
            if account:
                account.balance += balance_delta
                db.add(account)
        db.commit()
    else:
        db.rollback()
    
    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors[:20],
        "created_categories": created_categories,
        "created_accounts": created_accounts,
        "csv_type": csv_type
    }