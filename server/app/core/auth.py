"""
Authentication middleware and utilities for Clerk JWT validation.
"""

import logging
import jwt
import requests
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import wraps
from app.core.config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

# Cache for Clerk JWKS
_jwks_cache: Optional[dict] = None


def get_clerk_jwks() -> dict:
    """
    Fetch Clerk's JSON Web Key Set (JWKS) for JWT verification.
    Caches the result to avoid repeated requests.
    
    Returns:
        JWKS dictionary
    """
    global _jwks_cache
    
    if _jwks_cache is not None:
        return _jwks_cache
    
    if not settings.CLERK_PUBLISHABLE_KEY:
        logger.warning("CLERK_PUBLISHABLE_KEY not configured")
        return {}
    
    try:
        # Extract domain from publishable key (format: pk_test_...)
        # Clerk JWKS URL format: https://clerk.{domain}/.well-known/jwks.json
        # For development, use the Clerk dev instance URL
        jwks_url = f"https://{settings.CLERK_FRONTEND_API}/.well-known/jwks.json"
        
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        
        _jwks_cache = response.json()
        logger.info("Clerk JWKS fetched and cached")
        return _jwks_cache
        
    except Exception as e:
        logger.error(f"Failed to fetch Clerk JWKS: {e}")
        return {}


def verify_clerk_token(token: str) -> dict:
    """
    Verify Clerk JWT token and extract claims.
    
    Args:
        token: JWT token string
    
    Returns:
        Token claims dictionary
    
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Decode without verification first to get header
        unverified_header = jwt.get_unverified_header(token)
        
        # Get JWKS
        jwks = get_clerk_jwks()
        
        if not jwks:
            # If JWKS not available, decode without verification (dev mode only)
            if settings.DEBUG:
                logger.warning("DEBUG mode: Skipping JWT signature verification")
                claims = jwt.decode(token, options={"verify_signature": False})
                return claims
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="JWT verification unavailable"
                )
        
        # Find the matching key
        rsa_key = None
        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header["kid"]:
                rsa_key = key
                break
        
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Key not found"
            )
        
        # Verify and decode token
        claims = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=settings.CLERK_PUBLISHABLE_KEY,
            options={"verify_signature": True}
        )
        
        return claims
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTClaimsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token claims: {str(e)}"
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_user(request: Request) -> Optional[dict]:
    """
    Extract and verify user from request headers.
    
    Checks for:
    1. Authorization Bearer token (Clerk session JWT)
    2. X-User-ID header (for backward compatibility in dev mode)
    
    Args:
        request: FastAPI request object
    
    Returns:
        User dictionary with 'user_id' and other claims, or None if not authenticated
    """
    # Try Authorization header first
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
        try:
            claims = verify_clerk_token(token)
            user_id = claims.get("sub")  # Clerk puts user ID in 'sub' claim
            
            return {
                "user_id": user_id,
                "claims": claims,
                "authenticated": True
            }
        except HTTPException:
            # Token verification failed
            pass
    
    # Fallback to X-User-ID header (development only)
    if settings.DEBUG:
        user_id = request.headers.get("X-User-ID")
        if user_id:
            logger.warning(f"DEBUG mode: Using X-User-ID header for user {user_id}")
            return {
                "user_id": user_id,
                "claims": {},
                "authenticated": False  # Not truly authenticated
            }
    
    return None


async def require_auth(request: Request) -> dict:
    """
    Dependency that requires authentication.
    Raises 401 if user is not authenticated.
    
    Args:
        request: FastAPI request object
    
    Returns:
        User dictionary
    
    Raises:
        HTTPException: If not authenticated
    """
    user = await get_current_user(request)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


async def optional_auth(request: Request) -> Optional[dict]:
    """
    Dependency that allows optional authentication.
    Returns None if not authenticated, user dict if authenticated.
    
    Args:
        request: FastAPI request object
    
    Returns:
        User dictionary or None
    """
    return await get_current_user(request)
