#!/usr/bin/env python
"""Check MongoDB collections and data"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings

# Connect to MongoDB
db_name = settings.DATABASES['default']['NAME']
db_config = settings.DATABASES['default'].get('CLIENT', {})
host = db_config.get('host', 'localhost')
port = db_config.get('port', 27017)

client = MongoClient(host, port)
db = client[db_name]

print("="*60)
print("  MONGODB COLLECTIONS STATUS")
print("="*60)

collections = db.list_collection_names()
print(f"\nTotal Collections: {len(collections)}\n")

for coll_name in sorted(collections):
    count = db[coll_name].count_documents({})
    print(f"  {coll_name:<30} {count:>5} documents")

print("\n" + "="*60)
print("  DETAILED DATA")
print("="*60)

# Check specific collections
for coll in ['users_user', 'teams', 'games', 'game_results']:
    count = db[coll].count_documents({}) if coll in collections else 0
    print(f"\n{coll.upper()}: {count} documents")
    if count > 0:
        sample = db[coll].find_one()
        if sample and '_id' in sample:
            del sample['_id']
        print(f"  Sample: {list(sample.keys())[:5] if sample else 'None'}")

print("\n" + "="*60)
