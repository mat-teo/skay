# backend/auth.py
from datetime import datetime, timedelta,timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from database import get_db
from models import User

#HARDCODED CONFIG - CHANGE THIS IN PRODUCTION
SECRET_KEY = "your-secret-key-change-this-in-production"  # Almeno 32 caratteri
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme per proteggere le route
security = HTTPBearer(auto_error=False)


# ---------- PASSWORD ----------
def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, password_hash)
    

def get_password_hash(password: str) -> str:
    """Get the hash of a password."""
    return pwd_context.hash(password)


# ---------- TOKEN JWT ----------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with the given payload and expiration.
    """
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15)) 
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    

def decode_access_token(token: str) -> Optional[int]:
    """
    Decode a JWT access token and return the user ID.
    Returns None if the token is invalid or expired.
    """
    # SCRIVI TU: try/except con JWTError, estrai user_id da payload.get("sub")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return user_id
    except:
        return None
    


# ---------- AUTHENTICATION ENDPOINTS ----------
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency per proteggere le route.
    Prende token dal header Authorization: Bearer <token>
    Restituisce l'oggetto User o lancia HTTPException 401
    """
    # SCRIVI TU:
    # 1. Se credentials è None -> 401
    if credentials is None:
        raise HTTPException(status_code= 401, detail= "Credentials not found in header")
    # 2. token = credentials.credentials
    token = credentials.credentials
    # 3. user_id = decode_access_token(token) -> se None -> 401
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code = 401, detail="Invalid credentials")
    # 4. Query user dal DB: select(User).where(User.id == user_id)
    user = db.get(User, user_id)
    # 5. Se user non esiste -> 401
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    # 6. Restituisci user
    return user
    

