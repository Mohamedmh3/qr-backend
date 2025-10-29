"""
Views for the QR Access Verification System.
Implements all API endpoints for user management and QR verification.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.shortcuts import get_object_or_404

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserDetailSerializer,
    QRVerificationSerializer
)
from .jwt_utils import get_tokens_for_user, blacklist_token
from .mongodb_queries import MongoDBQueryHelper
from utils.error_handlers import handle_api_errors, log_api_request, validate_required_fields, validate_email_format, validate_password_strength, create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    """
    POST /api/register/
    
    Register a new user with automatic QR code generation.
    Returns user data with JWT token.
    """
    
    permission_classes = [permissions.AllowAny]
    
    @handle_api_errors
    @log_api_request
    def post(self, request):
        """
        Handle user registration.
        
        Request body:
            - name: User's full name
            - email: User's email address
            - password: User's password
            - password_confirm: Password confirmation
            
        Returns:
            - 201: User created successfully with tokens
            - 400: Validation error
        """
        serializer = UserRegistrationSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            tokens = get_tokens_for_user(user)
            
            # Prepare response data
            response_data = {
                'user': {
                    'id': str(user.id),
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'qr_id': user.qr_id,
                    'qr_image_url': user.get_qr_image_url(request),
                },
                'tokens': tokens,
                'message': 'User registered successfully'
            }
            
            logger.info(f"User registered successfully: {user.email}")
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    POST /api/login/
    
    Authenticate user and return JWT tokens.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Handle user login.
        
        Request body:
            - email: User's email address
            - password: User's password
            
        Returns:
            - 200: Login successful with tokens
            - 400: Invalid credentials
        """
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Log the user in (updates last_login)
            login(request, user)

            # Get QR code URL
            from utils.qr_generator import get_qr_code_url
            qr_url = get_qr_code_url(request, user.qr_id)

            # If QR URL is not available, try to regenerate
            if not qr_url:
                try:
                    from utils.qr_generator import generate_qr_code
                    file_path, file_content = generate_qr_code(user.qr_id, user.name)

                    # Save to media directory
                    from django.core.files.storage import default_storage
                    default_storage.save(file_path, file_content)

                    # Get URL again
                    qr_url = get_qr_code_url(request, user.qr_id)
                except Exception as e:
                    logger.error(f"Error generating QR code during login: {e}")
                    qr_url = None

            # Generate tokens
            tokens = get_tokens_for_user(user)

            # Prepare response
            response_data = {
                'user': {
                    'id': str(user.id),
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'qr_id': user.qr_id,
                    'qr_image_url': qr_url,
                },
                'tokens': tokens,
                'message': 'Login successful'
            }

            logger.info(f"User logged in: {user.email}")
            return Response(response_data, status=status.HTTP_200_OK)
        logger.warning(f"Login failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    POST /api/logout/
    
    Logout user by blacklisting their refresh token.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Handle user logout.
        
        Request body:
            - refresh: Refresh token to blacklist
            
        Returns:
            - 205: Logout successful
            - 400: Invalid token
        """
        try:
            refresh_token = request.data.get("refresh")
            
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Blacklist the token using our custom function
            if blacklist_token(refresh_token):
                logger.info(f"User logged out: {request.user.email if hasattr(request, 'user') and request.user.is_authenticated else 'Unknown'}")
                return Response(
                    {"message": "Logout successful"},
                    status=status.HTTP_205_RESET_CONTENT
                )
            else:
                # Since blacklisting is disabled, just return success
                logger.info("Token blacklisting disabled for MongoDB compatibility")
                return Response(
                    {"message": "Logout successful (token blacklisting disabled)"},
                    status=status.HTTP_205_RESET_CONTENT
                )
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"detail": "Invalid token or token already blacklisted"},
                status=status.HTTP_400_BAD_REQUEST
            )


class QRVerificationView(APIView):
    """
    GET /api/verify/<qr_id>/
    
    Verify a QR code and return user information.
    Used by Raspberry Pi for access verification.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, qr_id):
        """
        Verify QR code and return user information.
        
        Args:
            qr_id (str): QR ID to verify
            
        Returns:
            - 200: User found
            - 404: User not found
        """
        try:
            # Try Django ORM first (should work for simple queries)
            user = User.objects.filter(qr_id=qr_id, is_active=True).first()

            if user:
                response_data = {
                    'status': 'success',
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'qr_id': user.qr_id,
                    'message': 'User verified successfully'
                }

                logger.info(f"QR verification successful: {qr_id} - {user.email}")
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # Fallback to MongoDB helper if Django ORM fails
                try:
                    from utils.mongodb_queries import MongoDBQueryHelper
                    mongo_helper = MongoDBQueryHelper()
                    user = mongo_helper.get_user_by_qr_id(qr_id)

                    if user and user.is_active:
                        response_data = {
                            'status': 'success',
                            'name': user.name,
                            'email': user.email,
                            'role': user.role,
                            'qr_id': user.qr_id,
                            'message': 'User verified successfully'
                        }

                        logger.info(f"QR verification successful (MongoDB fallback): {qr_id} - {user.email}")
                        return Response(response_data, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error(f"MongoDB fallback failed: {e}")

                # User not found
                response_data = {
                    'status': 'failure',
                    'message': 'User not found or inactive'
                }

                logger.warning(f"QR verification failed: {qr_id}")
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"QR verification error: {e}")
            response_data = {
                'status': 'error',
                'message': 'Internal server error'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(APIView):
    """
    GET /api/users/
    
    List all users (admin endpoint).
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        List all users using custom MongoDB queries.
        """
        try:
            # Try Django ORM first
            users = User.objects.filter(is_active=True)

            # Serialize users
            serializer = UserSerializer(users, many=True, context={'request': request})

            return Response({
                'users': serializer.data,
                'count': users.count()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error listing users: {e}")
            # Fallback to MongoDB helper
            try:
                from utils.mongodb_queries import MongoDBQueryHelper
                mongo_helper = MongoDBQueryHelper()
                users = mongo_helper.get_all_users()

                serializer = UserSerializer(users, many=True, context={'request': request})

                return Response({
                    'users': serializer.data,
                    'count': len(users)
                }, status=status.HTTP_200_OK)

            except Exception as mongo_error:
                logger.error(f"MongoDB fallback also failed: {mongo_error}")
                return Response({
                    'error': 'Internal server error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        """
        List all users with pagination.
        
        Returns:
            - 200: List of users
            - 401: Unauthorized
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={'request': request}
        )
        
        logger.info(f"User list retrieved by: {request.user.email}")
        return Response({
            'count': queryset.count(),
            'users': serializer.data
        }, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveAPIView):
    """
    GET /api/users/<id>/
    
    Retrieve detailed information about a specific user.
    """
    
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """
        Return the queryset for user details.
        """
        # Try to use Django ORM first
        try:
            return User.objects.all()
        except Exception as e:
            logger.error(f"Error in UserDetailView queryset: {e}")
            # Return empty queryset as fallback
            return User.objects.none()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve user details.

        Returns:
            - 200: User details
            - 404: User not found
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, context={'request': request})

            logger.info(f"User detail retrieved: {instance.email} by {request.user.email}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving user detail: {e}")
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


class UserDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/users/<id>/
    
    Delete a user (admin endpoint).
    """
    
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a user and their QR code.

        Returns:
            - 200: User deleted successfully
            - 404: User not found
            - 403: Cannot delete yourself
        """
        try:
            instance = self.get_object()

            # Prevent users from deleting themselves
            if str(instance.id) == str(request.user.id):
                return Response(
                    {"detail": "You cannot delete your own account"},
                    status=status.HTTP_403_FORBIDDEN
                )

            user_email = instance.email
            self.perform_destroy(instance)

            logger.info(f"User deleted: {user_email} by {request.user.email}")
            return Response(
                {"message": f"User {user_email} deleted successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


class CurrentUserView(APIView):
    """
    GET /api/me/
    
    Get current authenticated user's information.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get current user information.
        
        Returns:
            - 200: Current user details
            - 401: Unauthorized
        """
        serializer = UserDetailSerializer(
            request.user,
            context={'request': request}
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)
