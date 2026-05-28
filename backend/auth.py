# backend/auth.py
"""
JWT Authentication module for Skay Finance API.
Handles password hashing, token creation, and user authentication.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from database import get_db
from models import User

# HARDCODED CONFIG - MOVE TO ENV VARIABLES IN PRODUCTION
SECRET_KEY = "your-secret-key-change-this-in-production"  # Minimum 32 characters
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme for protected routes (Bearer token)
security = HTTPBearer(auto_error=False)


# ==========================================
# PASSWORD HASHING UTILITIES
# ==========================================

def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify a plain text password against its hashed version.
    
    Args:
        plain_password: The password to verify (plain text)
        password_hash: The stored hash to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    """
    Generate a secure hash of a password using bcrypt.
    
    Args:
        password: The plain text password to hash
    
    Returns:
        A bcrypt hashed version of the password
    """
    return pwd_context.hash(password)


# ==========================================
# JWT TOKEN UTILITIES
# ==========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with expiration time.
    
    Args:
        data: Dictionary containing the claims to encode (must include 'sub' with user_id)
        expires_delta: Optional custom expiration time (defaults to 15 minutes)
    
    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[int]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token to decode
    
    Returns:
        The user_id (sub claim) if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        # Convert to int if present
        if user_id:
            return int(user_id)
        return None
    except JWTError:
        # Token expired or invalid signature
        return None


# ==========================================
# AUTHENTICATION DEPENDENCY
# ==========================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that extracts and validates the JWT token from the request.
    
    This function is used to protect routes by adding:
        current_user: User = Depends(get_current_user)
    
    Args:
        credentials: The HTTP Bearer token from the Authorization header
        db: Database session
    
    Returns:
        The authenticated User object
    
    Raises:
        HTTPException 401: If token is missing, invalid, expired, or user not found
    """
    # Step 1: Check if credentials header exists
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 2: Extract the token
    token = credentials.credentials
    
    # Step 3: Decode token and get user_id
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 4: Fetch user from database
    user = db.get(User, user_id)
    
    # Step 5: Verify user exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Step 6: Return authenticated user
    return user