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
        Transaction.type == "expense",
        Transaction.amount != 0
    )
    
    # Base statement for income
    income_stmt = select(func.sum(Transaction.amount)).where(
        Transaction.user_id == user_id,
        Transaction.type == "income",
        Transaction.amount != 0
    )

    # Apply date filters if provided
    if start_date:
        expense_stmt = expense_stmt.where(Transaction.date >= start_date, Transaction.amount != 0)
        income_stmt = income_stmt.where(Transaction.date >= start_date, Transaction.amount != 0)
    if end_date:
        expense_stmt = expense_stmt.where(Transaction.date <= end_date, Transaction.amount != 0)
        income_stmt = income_stmt.where(Transaction.date <= end_date, Transaction.amount != 0)

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
    """
    MAX_POINT_IN_RESULT = 25

    # Get all accounts for the user
    accounts = db.exec(select(Account).where(Account.user_id == user_id)).all()
    
    # Calculate current net worth (sum of all account balances)
    current_net_worth = sum(acc.balance for acc in accounts)
    
    # Determine date range
    today = datetime.now().date()
    range_start = start_date.date() if start_date else (today - timedelta(days=30))
    range_end = end_date.date() if end_date else today

    # Get all transactions from range_start up to TODAY. 
    # We do NOT filter by end_date here because we need all recent transactions 
    # to accurately calculate the net worth backwards from today's balance.
    query = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.date >= range_start,
        Transaction.amount != 0
    )
    transactions = db.exec(query.order_by(Transaction.date)).all()
    
    # Map date -> net worth change
    changes_by_date = defaultdict(float)
    for tx in transactions:
        change = tx.amount if tx.type == "income" else -tx.amount if tx.type == "expense" else 0
        date_key = tx.date.date() if hasattr(tx.date, 'date') else tx.date
        changes_by_date[date_key] += change
    
    # Reverse calculation: Start from TODAY's net worth and walk backwards to range_start
    running_net_worth = current_net_worth
    current_calc_date = today
    
    while current_calc_date >= range_start:
        if current_calc_date in changes_by_date:
            running_net_worth -= changes_by_date[current_calc_date]
        current_calc_date -= timedelta(days=1)
    
    # Build continuous date range from start to end
    all_dates = []
    current_date = range_start
    while current_date <= range_end:
        all_dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Build data points for every day moving forward
    data_points = []
    for date in all_dates:
        if date in changes_by_date:
            running_net_worth += changes_by_date[date]
        data_points.append({
            "date": date.isoformat(),
            "net_worth": round(running_net_worth, 2)
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
            date_object = date_object - timedelta(days=1)
            # Do not force net_worth to 0 here to prevent artificial chart spikes
            aggregated.insert(0, {"date": str(date_object), "net_worth": aggregated[0]["net_worth"]})

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
        # Use :02d to ensure single-digit months have a leading zero (e.g., "2024-02").
        # This is critical for correct alphabetical sorting.
        month_key = f"{date.year}-{date.month:02d}" 
        monthly[month_key] = point
    
    # Sort by date
    result = []
    for month_key in sorted(monthly.keys()):
        result.append(monthly[month_key])
    
    if len(result) == 1:
        date_object = datetime.strptime(result[0]["date"], "%Y-%m-%d").date()
        date_object = date_object.replace(day=1) - timedelta(days=1)
        key = f"{date_object.year}-{date_object.month:02d}"
        # Propagate the actual net worth instead of 0 to keep the chart line flat
        result.insert(0, {'date': key, 'net_worth': result[0]['net_worth']})
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
        # Since data_points are already in chronological order, 
        # we simply overwrite. The last one will be the end of the week.
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
    
    # Add an initial point before first week for better chart display
    if len(result) == 1:
        # Safely get the actual date from the original object
        first_date_str = list(weekly.values())[0]["date"]
        first_date = datetime.fromisoformat(first_date_str).date()
        
        # Calculate exactly the previous week based on the real year and month
        previous_week_end = first_date - timedelta(days=first_date.weekday() + 1)
        previous_week_start = previous_week_end - timedelta(days=6)
        
        # Propagate the actual net worth instead of 0
        result.insert(0, {
            "date": f"{previous_week_start.strftime('%d/%m')} - {previous_week_end.strftime('%d/%m')}",
            "net_worth": result[0]["net_worth"]
        })
    
    return result