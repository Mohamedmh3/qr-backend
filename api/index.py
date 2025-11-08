"""
Vercel serverless entry point for Django application
"""
import os
import sys
import traceback

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')

try:
    # Import Django WSGI application
    from qr_access_backend.wsgi import application
    app = application
    print("✓ Django application loaded successfully")
except Exception as e:
    print(f"✗ Error loading Django application: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    
    # Fallback error handler
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        error_msg = f'{{"error": "Django initialization failed", "details": "{str(e)}"}}'
        return [error_msg.encode()]
