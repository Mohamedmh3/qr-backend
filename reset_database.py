#!/usr/bin/env python
"""
Reset MongoDB database for fresh start after model changes.
Run: python reset_database.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings

def reset_database():
    """Drop all collections to start fresh"""
    print("\n" + "="*60)
    print("  RESETTING MONGODB DATABASE")
    print("="*60 + "\n")
    
    # Get MongoDB connection details
    db_name = settings.DATABASES['default']['NAME']
    db_config = settings.DATABASES['default'].get('CLIENT', {})
    host = db_config.get('host', 'localhost')
    port = db_config.get('port', 27017)
    
    try:
        # Connect to MongoDB
        client = MongoClient(host, port)
        db = client[db_name]
        
        print(f"Connected to MongoDB: {host}:{port}/{db_name}\n")
        
        # Get all collection names
        collections = db.list_collection_names()
        
        if not collections:
            print("No collections found. Database is already empty.\n")
            return
        
        print(f"Found {len(collections)} collections:")
        for coll in collections:
            print(f"  - {coll}")
        
        # Confirm before dropping
        response = input("\nDrop all collections? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            print("\nDropping collections...")
            for coll_name in collections:
                db[coll_name].drop()
                print(f"  ✓ Dropped: {coll_name}")
            
            print("\n" + "="*60)
            print("  DATABASE RESET COMPLETE")
            print("="*60)
            print("\nNext steps:")
            print("1. Run: python manage.py migrate")
            print("2. Run: python manage.py create_test_data")
            print("3. Run: python run_comprehensive_tests.py")
            print()
        else:
            print("\nOperation cancelled.")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure MongoDB is running:")
        print("  Windows: net start MongoDB")
        print("  Linux/Mac: sudo systemctl start mongod")

if __name__ == '__main__':
    reset_database()
