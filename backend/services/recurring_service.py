from datetime import datetime, timedelta
from typing import Optional
from models import RecurringTransaction

def add_months(date: datetime, months: int) -> datetime:
    """Add months to a date without using dateutil."""
    year = date.year + (date.month + months - 1) // 12
    month = (date.month + months - 1) % 12 + 1
    # Get last day of target month
    if month in [4, 6, 9, 11]:
        day = min(date.day, 30)
    elif month == 2:
        leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        day = min(date.day, 29 if leap else 28)
    else:
        day = date.day
    return date.replace(year=year, month=month, day=day)

def calculate_next_date(recurring: RecurringTransaction) -> datetime:
    """Calculate the next occurrence date based on frequency."""
    now = datetime.now()
    
    # Ensure start_date is datetime
    start_date = recurring.start_date
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    
    if recurring.frequency == "monthly":
        date = start_date.replace(day=recurring.day_of_month or 1)
        while date < now:
            date = add_months(date, 1)
        return date
    
    elif recurring.frequency == "weekly":
        today = now.weekday()
        target_day = recurring.day_of_week or 0
        days_ahead = target_day - today
        if days_ahead <= 0:
            days_ahead += 7
        return now + timedelta(days=days_ahead)
    
    elif recurring.frequency == "custom":
        months = recurring.custom_interval_months or 1
        date = start_date
        while date < now:
            date = add_months(date, months)
        return date
    
    return now

def advance_next_date(recurring: RecurringTransaction) -> datetime:
    """Advance the next_date by one period."""
    next_date = recurring.next_date
    if isinstance(next_date, str):
        next_date = datetime.fromisoformat(next_date.replace('Z', '+00:00'))
    
    if recurring.frequency == "monthly":
        return add_months(next_date, 1)
    elif recurring.frequency == "weekly":
        return next_date + timedelta(days=7)
    elif recurring.frequency == "custom":
        months = recurring.custom_interval_months or 1
        return add_months(next_date, months)
    return next_date