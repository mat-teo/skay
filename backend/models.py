from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from pydantic import validator

# ==========================================
# 1. USER MODELS (Input vs DB)
# ==========================================
class UserCreate(SQLModel):
    """Schema for user registration input."""
    email: str
    password: str
    base_currency: str = "EUR"

class User(SQLModel, table=True):
    """Database table representing a registered user."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index = True)
    password_hash: str
    base_currency: str = "EUR"
    # Future Auth/OTP management fields
    is_verified: bool = Field(default=False)
    otp_code: Optional[str] = Field(default=None)
    otp_expires_at: Optional[datetime] = Field(default=None)
    
    # Future Password Reset fields
    reset_token: Optional[str] = Field(default=None)
    reset_token_expires_at: Optional[datetime] = Field(default=None)

    is_2fa_enabled: bool = Field(default=False)
    otp_secret: Optional[str] = Field(default=None)

# ==========================================
# 2. ACCOUNT MODELS (Input vs DB)
# ==========================================
class AccountCreate(SQLModel):
    """Schema for creating a financial account."""
    name: str  # e.g., "Cash", "Bank Account"
    type: str  # e.g., "cash", "bank", "investment"
    balance: float = 0.0

class Account(AccountCreate, table=True):
    """Database table representing a financial account."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
# ==========================================
# 3. CATEGORY MODELS (Input vs DB)
# ==========================================
class TransactionCategoryCreate(SQLModel):
    """Schema for creating a transaction category."""
    name: str  # e.g., "Groceries", "Salary"
    type: str  # "income" or "expense"

class TransactionCategory(TransactionCategoryCreate, table=True):
    """Database table representing transaction categories."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int

# ==========================================
# 4. TRANSACTION MODELS (Input vs DB)
# ==========================================
class TransactionCreate(SQLModel):
    """Schema for recording a new transaction."""
    category_id: Optional[int] = None
    amount: float
    type: str  # "income", "expense", "transfer"
    date: Optional[datetime] = None  # Will default to current time if null
    notes: Optional[str] = None
    account_source_id: Optional[int] = None
    account_destination_id: Optional[int] = None

class Transaction(TransactionCreate, table=True):
    """Database table representing a transaction record."""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Redefining fields to strictly enforce foreign keys at database level
    user_id: int = Field(foreign_key="user.id", index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="transactioncategory.id")
    account_source_id: Optional[int] = Field(default=None, foreign_key="account.id")
    account_destination_id: Optional[int] = Field(default=None, foreign_key="account.id")
    recurring_id: Optional[int] = Field(default=None, foreign_key="recurring_transactions.id")

# ==========================================
# 5. STOCK PORTFOLIO MODELS
# ==========================================
class UserStockCreate(SQLModel):
    ticker: str
    quantity: float
    average_buy_price: float
    currency: str = "USD"
    
class UserStock(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    ticker: str = Field(index=True)
    quantity: float
    average_buy_price: float
    currency: str = Field(default="USD")

class StockPrice(SQLModel, table=True):
    ticker_or_currency: str = Field(primary_key=True)
    current_price: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# =======================
# Budgets
# =======================
class BudgetBase(SQLModel):
    name: str
    category_id: Optional[int] = None
    amount: float
    period: str  # 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase, table=True):
    __tablename__ = "budgets"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RecurringTransaction(SQLModel, table=True):
    __tablename__ = "recurring_transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    name: str
    amount: float
    type: str  # "income", "expense"
    category_id: int = Field(foreign_key="transactioncategory.id")  
    account_id: int = Field(foreign_key="account.id")  
    
    frequency: str  # "monthly", "weekly", "custom"
    custom_interval_months: Optional[int] = None
    day_of_month: Optional[int] = None
    day_of_week: Optional[int] = None
    
    start_date: datetime
    end_date: Optional[datetime] = None
    next_date: datetime 
    is_active: bool = True
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v < 0.01:
            raise ValueError('Amount must be greater than 0.01')
        return v
    
    @validator('category_id')
    def category_must_exist(cls, v):
        if v is None:
            raise ValueError('Category is required')
        return v
    
    @validator('account_id')
    def account_must_exist(cls, v):
        if v is None:
            raise ValueError('Account is required')
        return v