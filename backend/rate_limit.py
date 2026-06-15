import os
import sys
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Disable rate limiting for tests
TESTING = os.environ.get("TESTING") == "true" or "pytest" in sys.modules

if TESTING:
    # Create a no-op limiter that never limits
    class NoOpLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        def __call__(self, *args, **kwargs):
            return self
    
    limiter = NoOpLimiter()
else:
    limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

def setup_rate_limiting(app: FastAPI):
    """Configure rate limiting for the FastAPI app."""
    if not TESTING:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )