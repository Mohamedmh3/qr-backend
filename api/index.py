"""
Vercel serverless entry point for Django application
"""
import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

print(f"Python version: {sys.version}")
print(f"Project directory: {project_dir}")
print(f"sys.path: {sys.path[:3]}")

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_access_backend.settings')

# Import Django WSGI application
try:
    print("Importing Django setup...")
    import django
    print(f"Django version: {django.VERSION}")
    
    print("Setting up Django...")
    django.setup()
    
    print("Getting WSGI application...")
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
    
    print("✓ Django application loaded successfully")
except Exception as e:
    import traceback
    error_trace = traceback.format_exc()
    print(f"✗ FATAL ERROR: {e}")
    print(f"Full traceback:\n{error_trace}")
    
    # Create error response app
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [f"Django initialization failed:\n{error_trace}".encode()]
