from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel

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

# ==========================================
# 5. STOCK PORTFOLIO MODELS
# ==========================================
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