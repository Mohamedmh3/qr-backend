"""
Test MongoDB Atlas Connection
This script tests the connection to MongoDB Atlas and verifies database operations.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings
from users.models import User


def test_pymongo_connection():
    """Test direct PyMongo connection to MongoDB Atlas"""
    print("\n" + "="*60)
    print("TEST 1: Direct PyMongo Connection")
    print("="*60)
    
    try:
        # Get connection string from Django settings
        db_config = settings.DATABASES['default']
        connection_string = db_config['CLIENT']['host']
        db_name = db_config['NAME']
        
        print(f"📡 Connecting to MongoDB Atlas...")
        print(f"Database: {db_name}")
        
        # Create MongoDB client
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Get database
        db = client[db_name]
        
        # List collections
        collections = db.list_collection_names()
        print(f"\n📚 Collections found: {len(collections)}")
        for collection in collections:
            count = db[collection].count_documents({})
            print(f"  - {collection}: {count} documents")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def test_django_orm():
    """Test Django ORM with MongoDB Atlas"""
    print("\n" + "="*60)
    print("TEST 2: Django ORM Operations")
    print("="*60)
    
    try:
        # Count users
        user_count = User.objects.count()
        print(f"✅ User count: {user_count}")
        
        # Get first few users
        users = User.objects.all()[:5]
        print(f"\n👥 Sample users:")
        for user in users:
            print(f"  - {user.name} ({user.email}) - Role: {user.role}")
        
        # Test filtering
        admin_count = User.objects.filter(role='admin').count()
        staff_count = User.objects.filter(role='staff').count()
        player_count = User.objects.filter(role='player').count()
        
        print(f"\n📊 Users by role:")
        print(f"  - Admins: {admin_count}")
        print(f"  - Staff: {staff_count}")
        print(f"  - Players: {player_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django ORM test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database_write():
    """Test write operations to MongoDB Atlas"""
    print("\n" + "="*60)
    print("TEST 3: Database Write Test")
    print("="*60)
    
    try:
        # Try to create a test user
        test_email = "test_atlas@connection.com"
        
        # Delete if exists
        User.objects.filter(email=test_email).delete()
        print(f"🧹 Cleaned up any existing test user")
        
        # Create test user
        test_user = User.objects.create(
            name="Test Atlas User",
            email=test_email,
            role="user"
        )
        test_user.set_password("testpassword123")
        test_user.save()
        
        print(f"✅ Created test user: {test_user.name}")
        print(f"   User ID: {test_user.id}")
        print(f"   QR ID: {test_user.qr_id}")
        
        # Verify user was created
        retrieved_user = User.objects.get(email=test_email)
        print(f"✅ Retrieved test user: {retrieved_user.name}")
        
        # Clean up
        retrieved_user.delete()
        print(f"🧹 Deleted test user")
        
        return True
        
    except Exception as e:
        print(f"❌ Write test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 MONGODB ATLAS CONNECTION TEST")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("PyMongo Connection", test_pymongo_connection()))
    results.append(("Django ORM Read", test_django_orm()))
    results.append(("Database Write", test_database_write()))
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! MongoDB Atlas connection is working perfectly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
