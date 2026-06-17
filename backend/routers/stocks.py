# backend/routers/stocks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from typing import List
from database import get_db
from models import UserStock, UserStockCreate, User, StockPrice
from auth import get_current_user
from services.stock_service import get_stock_price_sync, calculate_portfolio_value
from rate_limit import limiter


router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/", response_model=List[UserStock])
@limiter.limit("10/minute")
def get_stocks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    statement = select(UserStock).where(UserStock.user_id == current_user.id)
    return db.exec(statement).all()

@router.post("/", response_model=UserStock)
@limiter.limit("5/minute")
def add_stock(stock: UserStockCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticker_upper = stock.ticker.upper()
    
    # STRICT VALIDATION: Check if market data exists for this asset
    if get_stock_price_sync(ticker_upper) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker '{ticker_upper}' not found. Please verify the symbol or add an exchange suffix if it is an international asset (e.g., '.DE' for Xetra, '.MI' for Milan, '.AS' for Amsterdam)."
        )
    
    existing = db.exec(
        select(UserStock).where(UserStock.user_id == current_user.id, UserStock.ticker == ticker_upper)
    ).first()
    
    if existing:
        total_quantity = existing.quantity + stock.quantity
        total_cost = (existing.quantity * existing.average_buy_price) + (stock.quantity * stock.average_buy_price)
        existing.average_buy_price = total_cost / total_quantity
        existing.quantity = total_quantity
        existing.currency = stock.currency or existing.currency
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    new_stock = UserStock(
        user_id=current_user.id,
        ticker=ticker_upper,
        quantity=stock.quantity,
        average_buy_price=stock.average_buy_price,
        currency=stock.currency or "USD"
    )
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock

@router.put("/{stock_id}", response_model=UserStock)
@limiter.limit("3/minute")
def update_stock(stock_id: int, stock_update: UserStockCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stock = db.get(UserStock, stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock record not found")
    if stock.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    ticker_upper = stock_update.ticker.upper()
    
    # STRICT VALIDATION
    if get_stock_price_sync(ticker_upper) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker '{ticker_upper}' not found. Please verify the symbol or add an exchange suffix if it is an international asset (e.g., '.DE' for Xetra)."
        )
    
    stock.ticker = ticker_upper
    stock.quantity = stock_update.quantity
    stock.average_buy_price = stock_update.average_buy_price
    stock.currency = stock_update.currency or stock.currency
    
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock

@router.delete("/{stock_id}")
def delete_stock(stock_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stock = db.get(UserStock, stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock record not found")
    if stock.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(stock)
    db.commit()
    return {"message": "Stock deleted successfully"}

@router.get("/portfolio")
@limiter.limit("10/minute")
def get_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stocks = db.exec(select(UserStock).where(UserStock.user_id == current_user.id)).all()
    if not stocks:
        return {"stocks": [], "summary": {"total_value": 0, "total_cost": 0, "total_gain": 0, "total_gain_percent": 0}}
    
    prices = {}
    has_errors = False
    
    for stock in stocks:
        price = get_stock_price_sync(stock.ticker)
        if price is not None:
            prices[stock.ticker] = price
        else:
            prices[stock.ticker] = 0.0
            has_errors = True
    
    result = []
    for stock in stocks:
        current_price = prices.get(stock.ticker, 0.0)
        current_value = current_price * stock.quantity
        cost = stock.average_buy_price * stock.quantity
        gain = current_value - cost
        gain_percent = (gain / cost * 100) if cost > 0 else 0
        
        result.append({
            "id": stock.id,
            "ticker": stock.ticker,
            "quantity": stock.quantity,
            "average_buy_price": stock.average_buy_price,
            "current_price": current_price,
            "current_value": current_value,
            "cost": cost,
            "gain": gain,
            "gain_percent": round(gain_percent, 2),
            "currency": stock.currency,
            "has_error": current_price == 0.0  # Tells UI if price loading failed
        })
    
    summary = calculate_portfolio_value(stocks, prices)
    
    return {
        "stocks": result,
        "summary": {
            "total_value": round(summary["total_value"], 2),
            "total_cost": round(summary["total_cost"], 2),
            "total_gain": round(summary["total_gain"], 2),
            "total_gain_percent": round(summary["total_gain_percent"], 2)
        },
        "has_pricing_errors": has_errors
    }

@router.post("/refresh-prices")
@limiter.limit("2/minute")
def refresh_prices(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stocks = db.exec(select(UserStock).where(UserStock.user_id == current_user.id)).all()
    updated = 0
    for stock in stocks:
        price = get_stock_price_sync(stock.ticker)
        if price:
            existing = db.get(StockPrice, stock.ticker)
            if existing:
                existing.current_price = price
                existing.last_updated = datetime.utcnow()
            else:
                db.add(StockPrice(ticker_or_currency=stock.ticker, current_price=price, last_updated=datetime.utcnow()))
            updated += 1
    db.commit()
    return {"message": f"Updated {updated} stock prices"}

@router.get("/value")
def get_stocks_value(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get total value of user's stock portfolio.
    """
    stocks = db.exec(
        select(UserStock).where(UserStock.user_id == current_user.id)
    ).all()
    
    total_value = 0
    for stock in stocks:
        price = get_stock_price_sync(stock.ticker)
        if price:
            total_value += price * stock.quantity
    
    return {
        "total_stock_value": round(total_value, 2)
    }