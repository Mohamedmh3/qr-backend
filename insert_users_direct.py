import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
import django
django.setup()

from django.conf import settings
from django.contrib.auth.hashers import make_password
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient(settings.DATABASES['default']['CLIENT']['host'], settings.DATABASES['default']['CLIENT']['port'])
db = client[settings.DATABASES['default']['NAME']]
col = db['users_user']

# Wipe existing
col.drop()

docs = [
    {
        '_id': ObjectId(),
        'id': 1,
        'email': 'admin@example.com',
        'name': 'Admin User',
        'role': 'admin',
        'password': make_password('AdminPass123!'),
        'qr_id': 'QR-ADMIN01',
        'qr_image': None,
        'is_active': True,
        'is_staff': True,
        'is_superuser': True,
        'date_joined': None,
        'last_login': None,
        'groups': [],
        'user_permissions': [],
    },
    {
        '_id': ObjectId(),
        'id': 2,
        'email': 'player1@example.com',
        'name': 'Player One',
        'role': 'user',
        'password': make_password('TestPass123!'),
        'qr_id': 'QR-USER01',
        'qr_image': None,
        'is_active': True,
        'is_staff': False,
        'is_superuser': False,
        'date_joined': None,
        'last_login': None,
        'groups': [],
        'user_permissions': [],
    }
]

col.insert_many(docs)
col.create_index([('email', 1)], unique=True, name='email_unique')
print('inserted users with fixed integer id (1,2)')





