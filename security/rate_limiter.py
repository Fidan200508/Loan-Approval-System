from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

# This tracks requests by IP address
limiter = Limiter(key_func=get_remote_address)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom message when someone hits the rate limit.
    Instead of a confusing error, we return a clear message.
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "message": "You are trying too many times. Please wait and try again.",
        }
    )