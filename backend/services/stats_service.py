from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from fastapi import HTTPException
from sqlmodel import Session, select, func
from models import User, Account, Transaction


def get_financial_stats(db: Session, user_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """
    Calculate filtered total income and expenses for a user within a specific timeframe.
    """
    # Base statement for expense
    expense_stmt = select(func.sum(Transaction.amount)).where(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    )
    
    # Base statement for income
    income_stmt = select(func.sum(Transaction.amount)).where(
        Transaction.user_id == user_id,
        Transaction.type == "income"
    )

    # Apply date filters if provided
    if start_date:
        expense_stmt = expense_stmt.where(Transaction.date >= start_date)
        income_stmt = income_stmt.where(Transaction.date >= start_date)
    if end_date:
        expense_stmt = expense_stmt.where(Transaction.date <= end_date)
        income_stmt = income_stmt.where(Transaction.date <= end_date)

    total_expense = db.exec(expense_stmt).one() or 0.0
    total_income = db.exec(income_stmt).one() or 0.0
    net_savings = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_savings": net_savings
    }


def get_net_worth_history(
    db: Session, 
    user_id: int, 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    interval: str = "month"  # day, week, month
) -> Dict[str, Any]:
    """
    Calculate net worth over time for charting.
    
    Returns a list of {date, net_worth} pairs with all dates filled.
    """
    
    MAX_POINT_IN_RESULT = 25

    # 1. Get all accounts with their current balance
    accounts = db.exec(select(Account).where(Account.user_id == user_id)).all()
    
    # 2. Get all transactions for date range
    query = select(Transaction).where(Transaction.user_id == user_id)
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    
    transactions = db.exec(query.order_by(Transaction.date)).all()
    
    # 3. Calculate current net worth (sum of all account balances)
    current_net_worth = sum(acc.balance for acc in accounts)
    
    # 4. Build a map of date -> net worth change
    changes_by_date = defaultdict(float)
    
    for tx in transactions:
        change = 0
        if tx.type == "expense":
            change = -tx.amount
        elif tx.type == "income":
            change = tx.amount
        # transfers: change = 0 (no net worth change)
        
        # Use date only (ignore time)
        date_key = tx.date.date() if hasattr(tx.date, 'date') else tx.date
        changes_by_date[date_key] += change
    
    # 5. Build continuous date range
    if not transactions:
        # No transactions, just return current net worth
        return {
            "data": [{"date": datetime.now().date().isoformat(), "net_worth": current_net_worth}],
            "interval": interval
        }
    
    sorted_change_dates = sorted(changes_by_date.keys())
    
    # Calculate net worth before the first transaction
    net_worth_before = current_net_worth
    for date in reversed(sorted_change_dates):
        net_worth_before -= changes_by_date[date]
    
    # Determine date range to fill
    first_date = sorted_change_dates[0]
    last_date = datetime.now().date()
    
    # Build all dates in range
    all_dates = []
    current_date = first_date
    while current_date <= last_date:
        all_dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Build data points for every day
    data_points = []
    running_net_worth = net_worth_before
    
    # Add day before first transaction
    day_before_first = first_date - timedelta(days=1)
    data_points.append({
        "date": day_before_first.isoformat(),
        "net_worth": running_net_worth
    })
    
    # Fill each day
    for date in all_dates:
        if date in changes_by_date:
            running_net_worth += changes_by_date[date]
        data_points.append({
            "date": date.isoformat(),
            "net_worth": running_net_worth
        })
    
    # 6. Aggregate by interval if needed
    if interval == "month":
        aggregated = aggregate_by_month(data_points)
    elif interval == "week":
        aggregated = aggregate_by_week(data_points)
    else:
        aggregated = data_points
        if len(aggregated) == 1:
            date_object = datetime.strptime(aggregated[0]["date"], "%Y-%m-%d").date()
            date_object = date_object - timedelta(1)
            aggregated.insert(0, {"date": str(date_object), "net_worth":0})

    if len(aggregated) > MAX_POINT_IN_RESULT:
        #Limiting the results to not have too many points in the graph
        aggregated = aggregated[-MAX_POINT_IN_RESULT:]

    return {
        "data": aggregated,
        "interval": interval,
        "start_date": data_points[0]["date"] if data_points else None,
        "end_date": data_points[-1]["date"] if data_points else None
    }


def aggregate_by_month(data_points: List[Dict]) -> List[Dict]:
    """Take last value of each month."""
    monthly = {}
    for point in data_points:
        date = datetime.fromisoformat(point["date"])
        month_key = f"{date.year}-{date.month}"
        # Keep the last occurrence of each month
        monthly[month_key] = point
    
    # Sort by date
    result = []
    for month_key in sorted(monthly.keys()):
        result.append(monthly[month_key])
    
    if len(result) == 1:
        date_object = datetime.strptime(result[0]["date"], "%Y-%m-%d").date()
        date_object = date_object.replace(day=1) - timedelta(1)
        key = f"{date_object.year}-{date_object.month}"
        result.insert(0, {'date': key,'net_worth':0})
    return result


def aggregate_by_week(data_points: List[Dict]) -> List[Dict]:
    """Take last value of each week."""
    weekly = {}
    for point in data_points:
        date = datetime.fromisoformat(point["date"])
        year, week, _ = date.isocalendar()
        week_key = f"{year}-{week:02d}"
        # Keep the last occurrence of each week
        weekly[week_key] = point
    
    # Sort by week
    result = []
    for week_key in sorted(weekly.keys()):
        result.append(weekly[week_key])

    if len(result) == 1:
        date_object = datetime.strptime(result[0]["date"], "%Y-%m-%d").date()
        date_object = date_object -timedelta(7)
        result.insert(0,{"date":date_object, "net_worth":0})
    return result