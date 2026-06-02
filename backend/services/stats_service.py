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
    interval: str = "month"
) -> Dict[str, Any]:
    """
    Calculate net worth over time for charting.
    
    Args:
        db: Database session
        user_id: Current user ID
        start_date: Start date filter (optional)
        end_date: End date filter (optional)
        interval: Aggregation level - 'day', 'week', or 'month'
    
    Returns:
        Dictionary with data points for chart
    """
    
    MAX_POINT_IN_RESULT = 25

    # Get all accounts for the user
    accounts = db.exec(select(Account).where(Account.user_id == user_id)).all()
    
    # Get all transactions within date range
    query = select(Transaction).where(Transaction.user_id == user_id)
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    
    transactions = db.exec(query.order_by(Transaction.date)).all()
    
    # Calculate current net worth (sum of all account balances)
    current_net_worth = sum(acc.balance for acc in accounts)
    
    # Map date -> net worth change
    changes_by_date = defaultdict(float)
    
    for tx in transactions:
        change = 0
        if tx.type == "expense":
            change = -tx.amount
        elif tx.type == "income":
            change = tx.amount
        
        date_key = tx.date.date() if hasattr(tx.date, 'date') else tx.date
        changes_by_date[date_key] += change
    
    # Determine date range
    # Priority: 1. User-provided dates, 2. First transaction, 3. Last 30 days
    if start_date:
        range_start = start_date.date()
    elif transactions:
        range_start = min(changes_by_date.keys())
    else:
        range_start = datetime.now().date() - timedelta(days=30)
    
    if end_date:
        range_end = end_date.date()
    else:
        range_end = datetime.now().date()
    
    # Calculate net worth at range_start
    # Start with current balance and subtract all changes that occurred after range_start
    running_net_worth = current_net_worth
    for date in sorted(changes_by_date.keys(), reverse=True):
        if date >= range_start:
            running_net_worth -= changes_by_date[date]
        else:
            break
    
    # Build continuous date range from start to end
    all_dates = []
    current_date = range_start
    while current_date <= range_end:
        all_dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Build data points for every day
    data_points = []
    
    for date in all_dates:
        if date in changes_by_date:
            running_net_worth += changes_by_date[date]
        data_points.append({
            "date": date.isoformat(),
            "net_worth": running_net_worth
        })
    
    # Aggregate by selected interval
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

    
    # Limit points for chart performance
    if len(aggregated) > MAX_POINT_IN_RESULT:
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
    """
    Aggregate daily data points into weekly buckets.
    Returns the last value of each week with pre-formatted date range labels.
    """
    weekly = {}
    
    # Collect last data point for each week
    for point in data_points:
        date = datetime.fromisoformat(point["date"])
        year, week, _ = date.isocalendar()
        week_key = f"{year}-{week:02d}"
        
        if week_key not in weekly:
            weekly[week_key] = point
        else:
            existing_date = datetime.fromisoformat(weekly[week_key]["date"])
            if date > existing_date:
                weekly[week_key] = point
    
    # Build result with formatted labels
    result = []
    for week_key in sorted(weekly.keys()):
        point = weekly[week_key]
        date_obj = datetime.fromisoformat(point["date"]).date()
        
        # Calculate Monday (start of week)
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Replace date with formatted label
        result.append({
            "date": f"{start_of_week.strftime('%d/%m')} - {end_of_week.strftime('%d/%m')}",
            "net_worth": point["net_worth"]
        })
    
    # Add a zero point before first week for better chart display
    if len(result) == 1:
        first_label = result[0]["date"]
        # Extract start date from first label
        first_start = first_label.split(" - ")[0]
        day, month = map(int, first_start.split('/'))
        # Calculate previous week's end date
        year = datetime.now().year
        first_date = datetime(year, month, day).date()
        previous_week_end = first_date - timedelta(days=1)
        previous_week_start = previous_week_end - timedelta(days=6)
        
        result.insert(0, {
            "date": f"{previous_week_start.strftime('%d/%m')} - {previous_week_end.strftime('%d/%m')}",
            "net_worth": 0
        })
    
    return result