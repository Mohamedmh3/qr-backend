"""
Custom MongoDB query methods to bypass djongo SQL translation issues.
Optimized for performance and error handling.
"""

from django.conf import settings
import pymongo
from bson import ObjectId
import logging
from typing import Optional, List
from django.core.cache import cache

logger = logging.getLogger(__name__)


class MongoDBQueryHelper:
    """
    Helper class for direct MongoDB queries to bypass djongo issues.
    """
    
    def __init__(self):
        self.client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        self.db = self.client[settings.DATABASES['default']['NAME']]
        self.collection = self.db['users_user']
    
    def get_user_by_email(self, email: str, include_password: bool = False) -> Optional[object]:
        """
        Get user by email using direct MongoDB query with caching.
        
        Args:
            email: User email address
            include_password: If True, include password hash (for authentication)
        """
        # Check cache first (but only if not including password, as cached users won't have password)
        if not include_password:
            cache_key = f"user_email_{email.lower()}"
            cached_user = cache.get(cache_key)
            if cached_user:
                logger.debug(f"User found in cache: {email}")
                return cached_user
        
        try:
            # Include password if needed for authentication
            projection = {} if include_password else {'password': 0}
            user_data = self.collection.find_one(
                {'email': email.lower()},
                projection
            )
            
            if user_data:
                user = self._create_user_from_data(user_data)
                
                # Only cache if password not included (for security)
                if not include_password:
                    cache_key = f"user_email_{email.lower()}"
                    cache.set(cache_key, user, 300)
                
                logger.info(f"User retrieved from MongoDB: {email}")
                return user
            return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def get_user_by_qr_id(self, qr_id):
        """
        Get user by QR ID using direct MongoDB query.
        """
        try:
            user_data = self.collection.find_one({'qr_id': qr_id, 'is_active': True})
            if user_data:
                # Convert MongoDB document to Django User instance
                from users.models import User
                user = User()
                
                # Properly set the MongoDB ObjectId
                user._id = user_data['_id']
                user.pk = str(user_data['_id'])
                
                # Set all user fields
                user.email = user_data.get('email', '')
                user.name = user_data.get('name', '')
                user.role = user_data.get('role', 'user')
                user.qr_id = user_data.get('qr_id', '')
                user.qr_image = user_data.get('qr_image', '')
                user.is_active = user_data.get('is_active', True)
                user.is_staff = user_data.get('is_staff', False)
                user.is_superuser = user_data.get('is_superuser', False)
                user.date_joined = user_data.get('date_joined')
                user.last_login = user_data.get('last_login')
                user.password = user_data.get('password', '')
                
                # Override the id property to return the MongoDB ObjectId
                def get_id():
                    return str(user_data['_id'])
                
                # Set the id property directly on the instance
                user.__dict__['id'] = get_id()
                
                logger.info(f"Created user with ObjectId: {user_data['_id']}")
                return user
            return None
        except Exception as e:
            logger.error(f"Error getting user by QR ID {qr_id}: {e}")
            return None
    
    def update_user_last_login(self, user_id, last_login):
        """
        Update user's last login time using direct MongoDB query.
        """
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'last_login': last_login}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
            return False
    
    def get_all_users(self):
        """
        Get all users using direct MongoDB query.
        """
        try:
            users = []
            for user_data in self.collection.find():
                from users.models import User
                user = User()
                user._id = user_data['_id']
                user.pk = str(user_data['_id'])  # Set primary key
                # Also set the id attribute directly
                user.__dict__['id'] = str(user_data['_id'])
                user.email = user_data.get('email', '')
                user.name = user_data.get('name', '')
                user.role = user_data.get('role', 'user')
                user.qr_id = user_data.get('qr_id', '')
                user.qr_image = user_data.get('qr_image', '')
                user.is_active = user_data.get('is_active', True)
                user.is_staff = user_data.get('is_staff', False)
                user.is_superuser = user_data.get('is_superuser', False)
                user.date_joined = user_data.get('date_joined')
                user.last_login = user_data.get('last_login')
                user.password = user_data.get('password', '')
                users.append(user)
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def delete_user(self, user_id):
        """
        Delete user using direct MongoDB query.
        """
        try:
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    def _create_user_from_data(self, user_data: dict) -> object:
        from users.models import User
        from utils.qr_generator import generate_qr_code, get_qr_code_url
        user = User()
        user._id = user_data.get('_id')
        user.pk = str(user._id)
        user.email = user_data.get('email', '')
        user.name = user_data.get('name', '')
        user.role = user_data.get('role', 'user')
        user.qr_id = user_data.get('qr_id', '')
        user.qr_image = user_data.get('qr_image', '')
        user.is_active = user_data.get('is_active', True)
        user.is_staff = user_data.get('is_staff', False)
        user.is_superuser = user_data.get('is_superuser', False)
        user.date_joined = user_data.get('date_joined')
        user.last_login = user_data.get('last_login')
        user.password = user_data.get('password', '')
        # Always MongoDB ObjectId hex string here
        user.__dict__['id'] = str(user._id) if user._id else None

        # Guarantee QR code file, prefer image
        if not user.qr_id:
            from utils.qr_generator import generate_unique_qr_id
            user.qr_id = generate_unique_qr_id()
            file_path, _ = generate_qr_code(user.qr_id, user.name)
            user.qr_image = file_path
            # PATCH: Save qr_image to DB so we never have null
            if user._id and user.qr_image:
                try:
                    self.collection.update_one(
                        {'_id': user._id},
                        {'$set': {'qr_id': user.qr_id, 'qr_image': user.qr_image}}
                    )
                except Exception as e:
                    logger.error(f"Failed to update qr_image after generation: {e}")
        else:
            qr_url = get_qr_code_url(None, user.qr_id)
            if not qr_url:
                # File missing, generate now
                file_path, _ = generate_qr_code(user.qr_id, user.name)
                user.qr_image = file_path
                # PATCH: Save qr_image to DB so we never have null
                if user._id and user.qr_image:
                    try:
                        self.collection.update_one(
                            {'_id': user._id},
                            {'$set': {'qr_image': user.qr_image}}
                        )
                    except Exception as e:
                        logger.error(f"Failed to update qr_image after regeneration: {e}")
            elif not user.qr_image:
                # DB missing qr_image, but file/qr_id exist
                user.qr_image = f"qr_codes/{user.qr_id}.png" # fallback, won't break SVG
                if user._id and user.qr_image:
                    try:
                        self.collection.update_one(
                            {'_id': user._id},
                            {'$set': {'qr_image': user.qr_image}}
                        )
                    except Exception as e:
                        logger.error(f"Failed to update qr_image fallback: {e}")
        return user
    
    def invalidate_user_cache(self, email: str = None, user_id: str = None):
        """
        Invalidate user cache entries.
        """
        if email:
            cache_key = f"user_email_{email.lower()}"
            cache.delete(cache_key)
        
        if user_id:
            cache_key = f"user_id_{user_id}"
            cache.delete(cache_key)
