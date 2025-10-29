"""
Script to migrate existing MongoDB data to Django format.
Handles the existing user data structure.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
django.setup()

from users.models import User
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)


def migrate_existing_users():
    """
    Migrate existing MongoDB users to Django format.
    """
    try:
        # Get all existing users from MongoDB
        existing_users = User.objects.all()
        logger.info(f"Found {existing_users.count()} existing users")
        
        for user in existing_users:
            logger.info(f"Processing user: {user.email}")
            
            # Update user fields if needed
            if not user.qr_id:
                from utils.qr_generator import generate_unique_qr_id
                user.qr_id = generate_unique_qr_id()
                logger.info(f"Generated QR ID for {user.email}: {user.qr_id}")
            
            # Ensure password is hashed
            if user.password and not user.password.startswith('pbkdf2_'):
                user.password = make_password(user.password)
                logger.info(f"Updated password hash for {user.email}")
            
            # Set default role if not set
            if not user.role:
                user.role = 'user'
                logger.info(f"Set default role for {user.email}")
            
            # Save the user
            user.save()
            logger.info(f"Updated user: {user.email}")
        
        logger.info("Migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise


if __name__ == "__main__":
    migrate_existing_users()


