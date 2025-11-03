import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')
import django
django.setup()

from django.conf import settings
from pymongo import MongoClient

client = MongoClient(settings.DATABASES['default']['CLIENT']['host'], settings.DATABASES['default']['CLIENT']['port'])
db = client[settings.DATABASES['default']['NAME']]
db.drop_collection('users_user')
print('dropped users_user')





