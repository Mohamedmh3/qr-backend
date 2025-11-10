#!/usr/bin/env python3
"""
Test script to:
1. Test MongoDB database connection
2. Test login with user credentials
3. Test score adjustment functionality
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
django.setup()

from django.conf import settings
from pymongo import MongoClient
from users.models import User, GameResult
from users.jwt_utils import get_tokens_for_user
from rest_framework_simplejwt.tokens import AccessToken
import traceback

def test_database_connection():
    """Test MongoDB connection"""
    print("=" * 80)
    print("TEST 1: Database Connection")
    print("=" * 80)
    
    try:
        mongo_uri = getattr(settings, 'MONGODB_URI', None)
        db_name = getattr(settings, 'MONGODB_DBNAME', 'qr_access_system')
        
        print(f"MongoDB URI: {mongo_uri[:50]}..." if mongo_uri and len(mongo_uri) > 50 else f"MongoDB URI: {mongo_uri}")
        print(f"Database Name: {db_name}")
        
        # Test connection
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Test basic operations
        collections = db.list_collection_names()
        print(f"\n✓ Connected successfully!")
        print(f"✓ Database: {db_name}")
        print(f"✓ Collections found: {len(collections)}")
        print(f"  Collections: {', '.join(collections[:10])}")
        
        # Test user collection
        users_collection = db['users_user']
        user_count = users_collection.count_documents({})
        print(f"✓ Users in database: {user_count}")
        
        # Check for the specific user
        test_user = users_collection.find_one({'email': 'momen123@gg.com'})
        if test_user:
            print(f"✓ Found user: momen123@gg.com")
            print(f"  User ID: {test_user.get('_id')}")
            print(f"  Name: {test_user.get('name')}")
            print(f"  Role: {test_user.get('role')}")
            print(f"  Is Active: {test_user.get('is_active')}")
            print(f"  Has Password: {'password' in test_user}")
        else:
            print(f"✗ User momen123@gg.com NOT FOUND in database")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        traceback.print_exc()
        return False


def test_user_login():
    """Test user login"""
    print("\n" + "=" * 80)
    print("TEST 2: User Login")
    print("=" * 80)
    
    email = "momen123@gg.com"
    password = "123"
    
    try:
        # Try to find user via Django ORM
        print(f"\nAttempting to find user: {email}")
        users = User.objects.filter(email=email)
        user = next((u for u in users if u.is_active), None)
        
        if not user:
            print("✗ User not found via Django ORM, trying MongoDB helper...")
            from users.mongodb_queries import MongoDBQueryHelper
            mongo_helper = MongoDBQueryHelper()
            user = mongo_helper.get_user_by_email(email)
        
        if not user:
            print("✗ User not found at all!")
            return False
        
        print(f"✓ User found: {user.email}")
        print(f"  User ID: {getattr(user, 'id', None) or getattr(user, 'pk', None)}")
        print(f"  Name: {user.name}")
        print(f"  Role: {user.role}")
        print(f"  Is Active: {user.is_active}")
        
        # Test password check
        print(f"\nTesting password check...")
        try:
            password_valid = user.check_password(password)
            print(f"  Password check result: {password_valid}")
            
            if not password_valid:
                print("✗ Password validation failed!")
                # Check what password hash is stored
                from pymongo import MongoClient
                client = MongoClient(settings.MONGODB_URI)
                db = client[settings.MONGODB_DBNAME]
                user_doc = db['users_user'].find_one({'email': email})
                if user_doc:
                    stored_password = user_doc.get('password', '')
                    print(f"  Stored password hash: {stored_password[:50]}...")
                client.close()
                return False
        except Exception as e:
            print(f"✗ Password check error: {e}")
            traceback.print_exc()
            return False
        
        print("✓ Password validation successful!")
        
        # Test token generation
        print(f"\nTesting JWT token generation...")
        try:
            tokens = get_tokens_for_user(user)
            print(f"✓ Tokens generated successfully!")
            print(f"  Access token: {tokens['access'][:50]}...")
            print(f"  Refresh token: {tokens['refresh'][:50]}...")
            
            # Decode token to verify
            access_token = AccessToken(tokens['access'])
            print(f"\n  Token claims:")
            print(f"    user_id: {access_token.get('user_id')}")
            print(f"    email: {access_token.get('email')}")
            print(f"    role: {access_token.get('role')}")
            
            # Test token validation
            print(f"\nTesting token validation...")
            from rest_framework_simplejwt.authentication import JWTAuthentication
            from rest_framework.request import Request
            from django.http import HttpRequest
            
            # Create a mock request
            mock_request = HttpRequest()
            mock_request.META['HTTP_AUTHORIZATION'] = f"Bearer {tokens['access']}"
            
            jwt_auth = JWTAuthentication()
            validated_user, validated_token = jwt_auth.authenticate(mock_request)
            
            if validated_user:
                print(f"✓ Token validation successful!")
                print(f"  Validated user: {validated_user.email}")
                print(f"  Validated user ID: {getattr(validated_user, 'id', None) or getattr(validated_user, 'pk', None)}")
            else:
                print(f"✗ Token validation failed!")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Token generation/validation error: {e}")
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"✗ Login test error: {e}")
        traceback.print_exc()
        return False


def test_score_adjustment():
    """Test score adjustment functionality"""
    print("\n" + "=" * 80)
    print("TEST 3: Score Adjustment")
    print("=" * 80)
    
    try:
        # Find a game result to test with
        print("\nLooking for game results...")
        results = GameResult.objects.all()[:5]
        results_list = list(results)
        
        if not results_list:
            print("✗ No game results found in database")
            return False
        
        result = results_list[0]
        print(f"✓ Found result: {result.result_id}")
        print(f"  User: {result.user.name} ({result.user.email})")
        print(f"  Game: {result.game.game_name if result.game else 'N/A'}")
        print(f"  Current score: {result.points_scored}")
        
        # Check serializer field name
        print(f"\nChecking serializer field names...")
        from users.serializers import GameResultSerializer
        serializer = GameResultSerializer(result)
        print(f"  Serializer fields: {list(serializer.fields.keys())}")
        print(f"  Serialized data keys: {list(serializer.data.keys())}")
        
        # Check if 'score' vs 'points_scored' mismatch
        if 'points_scored' in serializer.data:
            print(f"  ✓ Backend uses 'points_scored' field")
        if 'score' in serializer.data:
            print(f"  ✓ Backend also has 'score' field")
        
        # Test update
        print(f"\nTesting result update...")
        old_score = result.points_scored
        new_score = old_score + 10
        
        # Try updating via serializer
        update_data = {'points_scored': new_score, 'verified_by_admin': True}
        serializer = GameResultSerializer(result, data=update_data, partial=True)
        
        if serializer.is_valid():
            print(f"✓ Serializer validation passed")
            try:
                updated_result = serializer.save()
                print(f"✓ Result updated successfully!")
                print(f"  Old score: {old_score}")
                print(f"  New score: {updated_result.points_scored}")
            except Exception as e:
                print(f"✗ Save error: {e}")
                traceback.print_exc()
                return False
        else:
            print(f"✗ Serializer validation failed: {serializer.errors}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Score adjustment test error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("QR BACKEND DIAGNOSTIC TESTS")
    print("=" * 80)
    
    results = []
    
    # Test 1: Database connection
    results.append(("Database Connection", test_database_connection()))
    
    # Test 2: User login
    results.append(("User Login", test_user_login()))
    
    # Test 3: Score adjustment
    results.append(("Score Adjustment", test_score_adjustment()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 80)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - See details above")
    print("=" * 80)


if __name__ == '__main__':
    main()

