import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qr_access_backend.settings")
app = get_asgi_application()