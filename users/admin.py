"""
Django admin configuration for the User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for User model.
    """
    
    list_display = ('email', 'name', 'role', 'qr_id', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'name', 'qr_id')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'role')}),
        ('QR Information', {'fields': ('qr_id', 'qr_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('qr_id', 'qr_image', 'date_joined', 'last_login')
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly when editing existing users."""
        if obj:  # Editing an existing object
            return self.readonly_fields + ('email',)
        return self.readonly_fields
