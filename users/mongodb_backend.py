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
            # Include password for authentication
            user = mongo_helper.get_user_by_email(username, include_password=True)
            
            if user and user.check_password(password):
                logger.info(f"User authenticated: {user.email}")
                return user
            else:
                logger.warning(f"Authentication failed for: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID with MongoDB fallback.
        """
        User = get_user_model()
        try:
            # Try Django ORM first
            user = User.objects.filter(pk=user_id).first()
            if user:
                return user
        except Exception as e:
            logger.warning(f"ORM get_user failed for {user_id}: {e}")
        
        # Fallback to MongoDB direct query
        try:
            from .mongodb_queries import MongoDBQueryHelper
            from bson import ObjectId
            
            mongo_helper = MongoDBQueryHelper()
            # Try to get user by ObjectId
            try:
                user_data = mongo_helper.collection.find_one({'_id': ObjectId(user_id)})
            except:
                # If ObjectId conversion fails, try as string
                user_data = mongo_helper.collection.find_one({'_id': user_id})
            
            if user_data:
                user = mongo_helper._create_user_from_data(user_data)
                logger.info(f"User retrieved from MongoDB fallback: {user_id}")
                return user
        except Exception as e:
            logger.error(f"MongoDB fallback get_user failed for {user_id}: {e}")
        
        return None
