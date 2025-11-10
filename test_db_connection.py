#!/usr/bin/env python3
"""
Simple script to test MongoDB connection
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get MongoDB URI from environment or settings
mongo_uri = os.getenv('MONGODB_URI', 'mongodb+srv://syo358814_db_user:mK2hpHOWlxktrlX5@cluster0.8hto9nz.mongodb.net/qr_access_system?retryWrites=true&w=majority')
db_name = os.getenv('MONGODB_DBNAME', 'qr_access_system')

print("Testing MongoDB Connection...")
print(f"URI: {mongo_uri[:50]}...")
print(f"Database: {db_name}")

try:
    from pymongo import MongoClient
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    # Test connection
    collections = db.list_collection_names()
    print(f"\n✓ Connected successfully!")
    print(f"✓ Collections: {len(collections)}")
    
    # Check for user
    users_collection = db['users_user']
    user = users_collection.find_one({'email': 'momen123@gg.com'})
    
    if user:
        print(f"\n✓ User found: momen123@gg.com")
        print(f"  ID: {user.get('_id')}")
        print(f"  Name: {user.get('name')}")
        print(f"  Role: {user.get('role')}")
        print(f"  Active: {user.get('is_active')}")
    else:
        print(f"\n✗ User momen123@gg.com not found")
    
    client.close()
    print("\n✓ Connection test completed successfully!")
    
except Exception as e:
    print(f"\n✗ Connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

