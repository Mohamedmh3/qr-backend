"""
Custom JWT utilities for MongoDB ObjectId compatibility.
Handles the conversion between MongoDB ObjectIds and JWT tokens.
"""

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user, handling MongoDB ObjectId conversion.
    
    Args:
        user (User): User instance
        
    Returns:
        dict: Dictionary containing access and refresh tokens
    """
    try:
        # Convert primary key to string for JWT payload (pk is safest)
        user_id_val = getattr(user, 'pk', None) or getattr(user, 'id', None)
        user_id_str = str(user_id_val)
        
        # Create refresh token with custom claims
        refresh = RefreshToken()
        refresh['user_id'] = user_id_str
        refresh['email'] = user.email
        refresh['role'] = user.role
        
        # Create access token
        access = refresh.access_token
        access['user_id'] = user_id_str
        access['email'] = user.email
        access['role'] = user.role
        
        return {
            'refresh': str(refresh),
            'access': str(access),
        }
        
    except Exception as e:
        logger.error(f"Error generating tokens for user {user.email}: {e}")
        # Fallback to simple token generation
        refresh = RefreshToken()
        fallback_id = str(getattr(user, 'pk', None) or getattr(user, 'id', None))
        refresh['user_id'] = fallback_id
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


def blacklist_token(refresh_token_str):
    """
    Simple token validation (blacklisting disabled for MongoDB compatibility).
    
    Args:
        refresh_token_str (str): Refresh token string
        
    Returns:
        bool: True if token is valid format, False otherwise
    """
    try:
        # Just validate the token format
        token = RefreshToken(refresh_token_str)
        return True
    except Exception as e:
        logger.error(f"Invalid token format: {e}")
        return False
