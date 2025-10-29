"""
Custom permissions for role-based access control.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class to check if user has 'admin' role.
    """
    
    message = "You must be an admin to perform this action."
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated and has admin role.
        """
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'admin' or request.user.is_superuser)
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class allowing admins full access and regular users read-only.
    """
    
    message = "You must be an admin to modify this resource."
    
    def has_permission(self, request, view):
        """
        Allow read permissions for authenticated users,
        write permissions only for admins.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admins
        return request.user.role == 'admin' or request.user.is_superuser


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class allowing users to access their own data or admins to access all.
    """
    
    message = "You can only access your own data unless you are an admin."
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the owner of the object or an admin.
        """
        # Admin has full access
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
        
        # User can only access their own data
        return obj == request.user
