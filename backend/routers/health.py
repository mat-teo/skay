# backend/routers/health.py
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, text
from database import get_db

router = APIRouter(tags=["System"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for container orchestration and monitoring.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "unknown"
        }
    }
    
    try:
        db.exec(text("SELECT 1")).first()
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = "disconnected"
        health_status["error"] = str(e)
        return JSONResponse(status_code=503, content=health_status)
    
    return health_status