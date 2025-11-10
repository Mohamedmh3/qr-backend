"""
MongoDB query helper for bypassing djongo SQL-to-MongoDB conversion issues.
Provides direct MongoDB queries for critical operations.
"""

import os
from django.conf import settings
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)


class MongoDBQueryHelper:
    """
    Helper class for direct MongoDB queries to bypass djongo issues.
    """

    def __init__(self):
        """Initialize MongoDB connection."""
        try:
            # Get MongoDB URI and database name from settings
            mongo_uri = getattr(settings, 'MONGODB_URI', 'mongodb://localhost:27017/qr_access_db')
            db_name = getattr(settings, 'MONGODB_DBNAME', 'qr_access_system')

            # Connect to MongoDB
            self.client = MongoClient(mongo_uri)
            # Get database by name (extract from URI if present, otherwise use db_name)
            try:
                # Try to get database name from URI
                from urllib.parse import urlparse
                parsed = urlparse(mongo_uri)
                if parsed.path and parsed.path != '/':
                    db_name_from_uri = parsed.path.lstrip('/').split('?')[0]
                    if db_name_from_uri:
                        db_name = db_name_from_uri
            except Exception:
                pass  # Use db_name from settings
            
            self.db = self.client[db_name]

            # Get collection name (default to users)
            self.collection_name = getattr(settings, 'MONGODB_COLLECTION', 'users_user')
            self.collection = self.db[self.collection_name]

            logger.info(f"Connected to MongoDB: {self.db.name}")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_user_by_email(self, email):
        """
        Get user by email using direct MongoDB query.

        Args:
            email (str): User email

        Returns:
            User object or None
        """
        try:
            user_data = self.collection.find_one({'email': email.lower()})
            if user_data:
                # Convert MongoDB document to Django-like object
                from users.models import User

                # Create a mock user object
                user = User()
                user._id = user_data.get('_id')
                user.email = user_data.get('email')
                user.name = user_data.get('name')
                user.role = user_data.get('role', 'user')
                user.qr_id = user_data.get('qr_id')
                user.qr_image = user_data.get('qr_image')
                user.is_active = user_data.get('is_active', True)
                user.date_joined = user_data.get('date_joined')
                user.last_login = user_data.get('last_login')

                # Set the id property for JWT compatibility
                user.__dict__['id'] = str(user._id)

                return user
            return None

        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_qr_id(self, qr_id):
        """
        Get user by QR ID using direct MongoDB query.

        Args:
            qr_id (str): QR ID to search for

        Returns:
            User object or None
        """
        try:
            user_data = self.collection.find_one({'qr_id': qr_id})
            if user_data:
                # Convert MongoDB document to Django-like object
                from users.models import User

                user = User()
                user._id = user_data.get('_id')
                user.email = user_data.get('email')
                user.name = user_data.get('name')
                user.role = user_data.get('role', 'user')
                user.qr_id = user_data.get('qr_id')
                user.qr_image = user_data.get('qr_image')
                user.is_active = user_data.get('is_active', True)

                # Set the id property for JWT compatibility
                user.__dict__['id'] = str(user._id)

                # Add password checking capability
                user.set_password = lambda password: None  # Mock method
                user.check_password = lambda raw_password: self._check_password(user.email, raw_password)

                return user
            return None

        except Exception as e:
            logger.error(f"Error getting user by QR ID: {e}")
            return None

    def get_all_users(self):
        """
        Get all active users using direct MongoDB query.

        Returns:
            List of User objects
        """
        try:
            users_data = self.collection.find({'is_active': True})

            users = []
            from users.models import User

            for user_data in users_data:
                user = User()
                user._id = user_data.get('_id')
                user.email = user_data.get('email')
                user.name = user_data.get('name')
                user.role = user_data.get('role', 'user')
                user.qr_id = user_data.get('qr_id')
                user.qr_image = user_data.get('qr_image')
                user.is_active = user_data.get('is_active', True)
                user.date_joined = user_data.get('date_joined')
                user.last_login = user_data.get('last_login')

                # Add password checking capability
                user.set_password = lambda password: None  # Mock method
                user.check_password = lambda raw_password: self._check_password(user.email, raw_password)

                users.append(user)

            return users

        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    def update_user_last_login(self, email):
        """
        Update user's last login time.

        Args:
            email (str): User email

        Returns:
            bool: True if successful
        """
        try:
            from datetime import datetime
            result = self.collection.update_one(
                {'email': email.lower()},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False

    def _check_password(self, email, raw_password):
        """
        Check if raw password matches hashed password in database.

        Args:
            email (str): User email
            raw_password (str): Raw password to check

        Returns:
            bool: True if password matches
        """
        try:
            # For now, we'll need to implement proper password checking
            # This is a simplified version - in production you'd want proper password hashing
            from django.contrib.auth.hashers import check_password

            # Get the stored password hash from database
            user_data = self.collection.find_one({'email': email.lower()})
            if user_data and 'password' in user_data:
                return check_password(raw_password, user_data['password'])
            return False

        except Exception as e:
            logger.error(f"Error checking password: {e}")
            return False

    def close(self):
        """Close MongoDB connection."""
        try:
            if hasattr(self, 'client'):
                self.client.close()
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")


def get_mongodb_connection():
    """
    Get MongoDB connection helper instance.

    Returns:
        MongoDBQueryHelper: Helper instance
    """
    return MongoDBQueryHelper()
