#!/usr/bin/env python
"""
Test script to debug QR code generation and user registration issues.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
django.setup()

from users.models import User
from utils.qr_generator import generate_qr_code, get_qr_code_url
from django.core.files.storage import default_storage
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_qr_generation():
    """Test QR code generation directly."""
    print("=== Testing QR Code Generation ===")

    # Test generate_unique_qr_id
    qr_id = generate_qr_code("TEST-QR123", "Test User")
    print(f"Generated QR ID: {qr_id}")

    # Test QR code generation
    try:
        file_path, file_content = generate_qr_code("TEST-QR123", "Test User")
        print(f"Generated file path: {file_path}")
        print(f"File content type: {type(file_content)}")

        # Save the file
        saved_path = default_storage.save(file_path, file_content)
        print(f"Saved to: {saved_path}")

        # Check if file exists
        if default_storage.exists(saved_path):
            print("✅ File saved successfully")

            # Test URL generation
            from django.test import RequestFactory
            factory = RequestFactory()
            request = factory.get('/')

            url = get_qr_code_url(request, "TEST-QR123")
            print(f"Generated URL: {url}")
        else:
            print("❌ File not saved")

    except Exception as e:
        print(f"❌ QR generation failed: {e}")
        import traceback
        traceback.print_exc()


def test_user_creation():
    """Test user creation with QR code."""
    print("\n=== Testing User Creation ===")

    try:
        # Create a test user
        user = User.objects.create_user(
            email="test@example.com",
            name="Test User",
            password="Test123!",
            role="user"
        )

        print(f"✅ User created: {user.email}")
        print(f"   QR ID: {user.qr_id}")
        print(f"   QR Image: {user.qr_image}")
        print(f"   User ID: {user.id}")

        # Test QR URL
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')

        url = user.get_qr_image_url(request)
        print(f"   QR URL: {url}")

        # Clean up
        user.delete()
        print("✅ Test user cleaned up")

    except Exception as e:
        print(f"❌ User creation failed: {e}")
        import traceback
        traceback.print_exc()


def test_database_connection():
    """Test database connection and queries."""
    print("\n=== Testing Database Connection ===")

    try:
        # Test simple query
        user_count = User.objects.count()
        print(f"Total users in database: {user_count}")

        # Test email query (the problematic one)
        email_query = User.objects.filter(email="test@example.com").first()
        print(f"Email query result: {email_query}")

        print("✅ Database connection working")

    except Exception as e:
        print(f"❌ Database query failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting QR Code and User Registration Tests...")

    test_database_connection()
    test_qr_generation()
    test_user_creation()

    print("\n=== Tests Complete ===")
