"""
Custom MongoDB backend to handle existing data and fix djongo issues.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import models
import logging

logger = logging.getLogger(__name__)


class MongoDBUserBackend(ModelBackend):
    """
    Custom authentication backend for MongoDB users.
    Handles existing data structure and djongo compatibility issues.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with MongoDB data using custom queries.
        """
        if username is None or password is None:
            return None
        
        try:
            # Use custom MongoDB query helper
            from .mongodb_queries import MongoDBQueryHelper
            mongo_helper = MongoDBQueryHelper()
            user = mongo_helper.get_user_by_email(username)
            
            if user and user.check_password(password):
                logger.info(f"User authenticated: {user.email}")
                return user
            else:
                logger.warning(f"Authentication failed for: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID.
        """
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
