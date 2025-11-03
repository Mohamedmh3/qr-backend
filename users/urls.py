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
    DebugLoginView,
    TeamListCreateView,
    TeamDetailView,
    GameListView,
    GameResultListCreateView,
    AdminGameManagementView,
    AdminResultManagementView,
)

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('debug/login/', DebugLoginView.as_view(), name='debug-login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # QR verification endpoint (for Raspberry Pi)
    path('verify/<str:qr_id>/', QRVerificationView.as_view(), name='verify'),
    
    # User management endpoints (admin)
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<str:id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<str:id>/delete/', UserDeleteView.as_view(), name='user-delete'),
    
    # Current user endpoint
    path('me/', CurrentUserView.as_view(), name='current-user'),

    # Team management
    path('teams/', TeamListCreateView.as_view(), name='team-list-create'),
    # Accept no-trailing-slash to avoid APPEND_SLASH redirect issues on POST
    path('teams', TeamListCreateView.as_view(), name='team-list-create-noslash'),
    path('teams/<str:team_id>/', TeamDetailView.as_view(), name='team-detail'),
    
    # Game management
    path('games/', GameListView.as_view(), name='game-list'),
    
    # Game results
    path('results/', GameResultListCreateView.as_view(), name='result-list-create'),
    path('results', GameResultListCreateView.as_view(), name='result-list-create-noslash'),

    # Admin endpoints
    path('admin/games/', AdminGameManagementView.as_view(), name='admin-game-create'),
    path('admin/games/<str:game_id>/', AdminGameManagementView.as_view(), name='admin-game-update'),
    path('admin/results/', AdminResultManagementView.as_view(), name='admin-result-list'),
    path('admin/results/<str:result_id>/', AdminResultManagementView.as_view(), name='admin-result-update'),
]
