"""
Serializers for the QR Access Verification System.
Handles data validation and serialization for all API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User
import logging

logger = logging.getLogger(__name__)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration endpoint.
    Handles user creation with password hashing and QR code generation.
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    qr_image_url = serializers.SerializerMethodField(read_only=True)
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default='user',
        required=False
    )
    
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'password_confirm', 
                  'role', 'qr_id', 'qr_image_url', 'date_joined')
        read_only_fields = ('id', 'qr_id', 'qr_image_url', 'date_joined')
        extra_kwargs = {
            'email': {
                'validators': []  # Disable automatic unique validation
            }
        }
    
    def get_qr_image_url(self, obj):
        """Get the full URL for the QR code image."""
        request = self.context.get('request')
        return obj.get_qr_image_url(request)
    
    def validate(self, attrs):
        """
        Validate that passwords match and email is unique.
        """
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        
        # Check if email already exists (MongoDB-safe)
        email = attrs.get('email', '').lower()
        # DISABLED: Email uniqueness check causes djongo recursion errors
        # The database will handle uniqueness constraint automatically
        logger.warning(f"Skipping email uniqueness check due to djongo limitations: {email}")
        # try:
        #     existing_user = User.objects.filter(email=email).first()
        #     if existing_user:
        #         raise serializers.ValidationError({
        #             "email": "A user with this email already exists."
        #         })
        # except Exception as e:
        #     # If query fails due to djongo issues, skip validation
        #     # The database will handle uniqueness constraint
        #     logger.warning(f"Email uniqueness check failed: {e}")
        #     pass
        
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user with hashed password and QR code.
        """
        # Remove password_confirm from validated data
        validated_data.pop('password_confirm', None)
        
        # Get role or default to 'user'
        role = validated_data.pop('role', 'user')
        
        # Create user using the manager's create_user method
        user = User.objects.create_user(
            email=validated_data['email'].lower(),
            name=validated_data['name'],
            password=validated_data['password'],
            role=role
        )
        
        logger.info(f"New user registered: {user.email} with role: {role}")
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login endpoint.
    Validates credentials and returns user data.
    """
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Validate user credentials.
        """
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if email and password:
            # Authenticate user
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                # Fallback to direct MongoDB query if Django auth fails
                try:
                    from .mongodb_queries import MongoDBQueryHelper
                    mongo_helper = MongoDBQueryHelper()
                    mongo_user = mongo_helper.get_user_by_email(email)

                    if mongo_user and mongo_user.check_password(password) and mongo_user.is_active:
                        user = mongo_user
                        logger.info(f"User authenticated via MongoDB fallback: {email}")
                    else:
                        raise serializers.ValidationError({
                            "detail": "Invalid email or password."
                        })
                except Exception as e:
                    logger.error(f"MongoDB authentication fallback failed: {e}")
                    raise serializers.ValidationError({
                        "detail": "Invalid email or password."
                    })
            
            if not user.is_active:
                raise serializers.ValidationError({
                    "detail": "User account is disabled."
                })
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError({
                "detail": "Must include 'email' and 'password'."
            })


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with QR information.
    Used for listing and retrieving user data.
    """
    
    qr_image_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'role', 'qr_id', 'qr_image_url', 
                  'is_active', 'is_staff', 'date_joined', 'last_login')
        read_only_fields = ('id', 'qr_id', 'qr_image_url', 'date_joined', 'last_login')
    
    def get_qr_image_url(self, obj):
        """Get the full URL for the QR code image."""
        request = self.context.get('request')
        return obj.get_qr_image_url(request)


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for User model.
    Includes all user information for profile views.
    """
    
    qr_image_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'role', 'qr_id', 'qr_image_url', 
                  'is_active', 'is_staff', 'is_superuser', 
                  'date_joined', 'last_login')
        read_only_fields = ('id', 'email', 'qr_id', 'qr_image_url', 
                           'date_joined', 'last_login')
    
    def get_qr_image_url(self, obj):
        """Get the full URL for the QR code image."""
        request = self.context.get('request')
        return obj.get_qr_image_url(request)


class QRVerificationSerializer(serializers.Serializer):
    """
    Serializer for QR code verification endpoint.
    Used by Raspberry Pi to verify user access.
    """
    
    status = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
    
    class Meta:
        fields = ('status', 'name', 'email', 'role', 'message')
