"""
App configuration for the users application.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for users app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'User Management'
