"""
Rate limiting middleware using SlowAPI.
"""

import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_identifier(request):
    """
    Get identifier for rate limiting.
    Uses user ID from auth if available, otherwise IP address.
    """
    # Try to get user ID from request state (set by auth middleware)
    if hasattr(request.state, "user") and request.state.user:
        user_id = request.state.user.get("user_id")
        if user_id:
            return f"user:{user_id}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=[
        f"{settings.RATE_LIMIT_PER_MINUTE}/minute",
        f"{settings.RATE_LIMIT_PER_HOUR}/hour"
    ],
    storage_uri="memory://",  # In-memory storage (use Redis for production)
    strategy="fixed-window"
)
