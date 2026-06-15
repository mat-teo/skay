# backend/routers/auth.py
"""
Authentication routes for user registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from slowapi.util import get_remote_address 
from datetime import timedelta
from logger import setup_logger

from database import get_db
from models import User, UserCreate
from auth import (
    verify_password, 
    create_access_token, 
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["authentication"])

logger = setup_logger(__name__)

@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.
    
    OAuth2PasswordRequestForm expects 'username' and 'password' fields.
    This implementation uses email as the username.
    """
    logger.info(f"Login attempt for email: {form_data.username}")

    # Step 1: Find user by email
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()
    
    # Step 2: Raise 401 if user not found
    if not user:
        logger.warning(f"Login failed: user not found - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 3: Verify password
    if not verify_password(form_data.password, user.password_hash):
        logger.warning(f"Login failed: wrong password - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 4: Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    logger.info(f"Login successful: {form_data.username}")
    # Step 5: Return token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: Request,
    user_data: UserCreate, 
    session: Session = Depends(get_db)
):
    """
    Register a new user with hashed password.
    
    - Checks if email already exists
    - Hashes the password before storing
    - Returns user object without password field
    """
    logger.info(f"Registration attempt for email: {user_data.email}")
    # Step 1: Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        logger.warning(f"Registration failed: email already registered - {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Step 2: Create new user with hashed password
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        base_currency=user_data.base_currency
    )
    
    # Step 3: Save to database
    session.add(user)
    session.commit()
    session.refresh(user)  # Get the auto-generated ID
    
    # Step 4: Return user without password
    # (User model doesn't expose password by design)
    logger.info(f"Registration successful: {user_data.email}")
    return user