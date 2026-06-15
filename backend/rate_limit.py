import os
import sys
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Disable rate limiting for tests
TESTING = os.environ.get("TESTING") == "true" or "pytest" in sys.modules

limiter = Limiter(key_func=get_remote_address,
                  enabled = not TESTING)

def setup_rate_limiting(app: FastAPI):
    """Configure rate limiting for the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )