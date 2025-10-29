"""
URL configuration for the users app.
Defines all API endpoints for the QR Access Verification System.
"""

from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    QRVerificationView,
    UserListView,
    UserDetailView,
    UserDeleteView,
    CurrentUserView,
)

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # QR verification endpoint (for Raspberry Pi)
    path('verify/<str:qr_id>/', QRVerificationView.as_view(), name='verify'),
    
    # User management endpoints (admin)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<str:id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<str:id>/delete/', UserDeleteView.as_view(), name='user-delete'),
    
    # Current user endpoint
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
