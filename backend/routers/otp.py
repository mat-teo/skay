# backend/routers/otp.py
import pyotp
import qrcode
from io import BytesIO
import base64
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from datetime import datetime, timedelta
import jwt
import os

from database import get_db
from models import User
from auth import get_current_user, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth/2fa", tags=["2FA"])

def create_temp_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "2fa_temp"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_temp_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "2fa_temp":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/status")
def get_2fa_status(current_user: User = Depends(get_current_user)):
    return {"is_enabled": current_user.is_2fa_enabled}

@router.post("/setup")
def setup_2fa(current_user: User = Depends(get_current_user)):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.email,
        issuer_name="Skay Finance"
    )
    
    qr = qrcode.make(provisioning_uri)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return {"secret": secret, "qr_code": f"data:image/png;base64,{qr_base64}"}

@router.post("/verify")
def verify_and_enable_2fa(
    request_data: dict, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    secret = request_data.get("secret")
    token = request_data.get("token")

    if not secret or not token:
        raise HTTPException(status_code=400, detail="Missing secret or token")

    totp = pyotp.TOTP(secret)
    if not totp.verify(token):
        raise HTTPException(status_code=400, detail="Invalid OTP token")
    
    current_user.otp_secret = secret
    current_user.is_2fa_enabled = True
    db.add(current_user)
    db.commit()
    return {"message": "2FA enabled successfully"}

@router.post("/disable")
def disable_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.otp_secret = None
    current_user.is_2fa_enabled = False
    db.add(current_user)
    db.commit()
    return {"message": "2FA disabled successfully"}

@router.post("/login")
def verify_2fa_login(
    request_data: dict, 
    db: Session = Depends(get_db)
):
    temp_token = request_data.get("temp_token")
    otp_token = request_data.get("otp_token")

    print(f"Received temp_token: {temp_token[:20]}...")
    print(f"Received otp_token: {otp_token}")
    
    user_id = verify_temp_token(temp_token)
    print(f"User ID from token: {user_id}")
    
    user = db.get(User, user_id)
    if not user:
        print("User not found")
        raise HTTPException(status_code=401, detail="User not found")
    
    print(f"User: {user.email}, 2FA enabled: {user.is_2fa_enabled}")
    
    if not user.is_2fa_enabled:
        print("2FA not enabled")
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    totp = pyotp.TOTP(user.otp_secret)
    print(f"Verifying OTP: {otp_token} against secret: {user.otp_secret[:10]}...")
    
    if not totp.verify(otp_token):
        print("Invalid OTP token")
        raise HTTPException(status_code=400, detail="Invalid OTP token")
    
    from auth import create_access_token
    access_token = create_access_token(data={"sub": str(user.id)})
    print("Access token created successfully")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }