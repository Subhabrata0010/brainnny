"""
User router - Handles user profile management.
POST /user - Create or get user profile.
GET /user/{user_id} - Get user profile.
PUT /user/{user_id} - Update user profile.
"""

import logging
from fastapi import APIRouter, HTTPException
from app.services.memory_service import MemoryService
from app.models.schemas import UserProfileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/{user_id}", response_model=UserProfileResponse)
def create_or_get_user(user_id: str):
    """
    Create a new user profile or get existing one.
    This should be called when a user first signs in via Clerk.
    
    Args:
        user_id: User identifier (from Clerk)
    
    Returns:
        UserProfileResponse with user profile data
    """
    try:
        logger.info(f"Creating or getting user profile for {user_id}")
        
        # Ensure user exists
        MemoryService._ensure_user_exists(user_id)
        
        # Get and return profile
        profile = MemoryService.get_user_profile(user_id)
        
        if profile:
            return profile
        
        # If for some reason it doesn't exist, return a default
        return UserProfileResponse(
            user_id=user_id,
            communication_style=None,
            recurring_topics=[],
            preferences={}
        )
        
    except Exception as e:
        logger.error(f"Error creating/getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user(user_id: str):
    """
    Get user profile.
    
    Args:
        user_id: User identifier
    
    Returns:
        UserProfileResponse with user profile data
    """
    try:
        profile = MemoryService.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
