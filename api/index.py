"""
Vercel serverless entry point for Django application
"""
import os
import sys

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')

# Import Django WSGI application
from qr_access_backend.wsgi import application

# Vercel handler
app = application
