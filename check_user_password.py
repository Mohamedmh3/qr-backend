#!/usr/bin/env python3
"""
Check user password hash in database
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from pymongo import MongoClient

mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://syo358814_db_user:mK2hpHOWlxktrlX5@cluster0.8hto9nz.mongodb.net/qr_access_system?retryWrites=true&w=majority')
db_name = os.getenv('MONGODB_DBNAME', 'qr_access_system')

email = 'momen123@gg.com'

print(f"Checking user: {email}")
print(f"Database: {db_name}")

try:
    client = MongoClient(mongo_uri)
    db = client[db_name]
    users_collection = db['users_user']
    
    user = users_collection.find_one({'email': email.lower()})
    
    if user:
        print(f"\n✓ User found:")
        print(f"  ID: {user.get('_id')}")
        print(f"  Name: {user.get('name')}")
        print(f"  Email: {user.get('email')}")
        print(f"  Role: {user.get('role')}")
        print(f"  Active: {user.get('is_active')}")
        
        password_hash = user.get('password', '')
        if password_hash:
            print(f"\n✓ Password hash found:")
            print(f"  Length: {len(password_hash)}")
            print(f"  First 30 chars: {password_hash[:30]}...")
            print(f"  Format: {'pbkdf2' if password_hash.startswith('pbkdf2_sha256') else 'other'}")
            
            # Test password check
            print(f"\nTesting password check with Django...")
            try:
                import django
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
                django.setup()
                
                from django.contrib.auth.hashers import check_password
                
                test_password = '123'
                result = check_password(test_password, password_hash)
                print(f"  Password '123' check: {'✓ MATCH' if result else '✗ NO MATCH'}")
                
                # Also try with the User model
                from users.models import User
                user_obj = User()
                user_obj.password = password_hash
                result2 = user_obj.check_password(test_password)
                print(f"  User.check_password('123'): {'✓ MATCH' if result2 else '✗ NO MATCH'}")
                
            except Exception as e:
                print(f"  Error testing password: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n✗ No password hash found in database!")
    else:
        print(f"\n✗ User not found!")
    
    client.close()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

