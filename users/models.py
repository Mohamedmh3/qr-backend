"""
User models for the QR Access Verification System.
Custom user model with QR code functionality.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import datetime
import uuid
import os
from utils.qr_generator import generate_unique_qr_id, generate_qr_code, delete_qr_code
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    """
    Custom user manager for handling user creation.
    """
    
    def create_user(self, email, name, password=None, **extra_fields):
        """
        Create and save a regular user with the given email, name, and password.
        
        Args:
            email (str): User's email address
            name (str): User's full name
            password (str): User's password
            
        Returns:
            User: Created user instance
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not name:
            raise ValueError('Users must have a name')
        
        email = self.normalize_email(email)
        
        # Create new user
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None, **extra_fields):
        """
        Create and save a superuser with the given email, name, and password.
        
        Args:
            email (str): Admin's email address
            name (str): Admin's full name
            password (str): Admin's password
            
        Returns:
            User: Created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')  # Superusers are admins
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with QR code functionality.
    Each user has a unique QR ID and corresponding QR code image.
    """
    
    # Role choices
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    # User identification fields
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True,
    )
    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        db_index=True,
        help_text="User role: 'user' or 'admin'"
    )
    
    # QR code fields
    qr_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False,
        help_text="Unique QR identifier for this user"
    )
    qr_image = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Path to the QR code image"
    )
    
    # Permission fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamp fields
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Manager
    objects = UserManager()
    
    # Authentication field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    @property
    def id(self):
        """
        Return the MongoDB ObjectId as string.
        """
        # Check if id is already set in __dict__
        if 'id' in self.__dict__:
            return self.__dict__['id']
        
        # Fallback to _id or pk
        if hasattr(self, '_id') and self._id:
            return str(self._id)
        elif hasattr(self, 'pk') and self.pk:
            return str(self.pk)
        
        return super().id
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate QR ID and QR code on creation.
        """
        # Handle update_fields parameter for last_login updates
        if 'update_fields' in kwargs and 'last_login' in kwargs['update_fields']:
            # For last_login updates, just call parent save
            return super().save(*args, **kwargs)
        
        # Generate QR ID if this is a new user
        if not self.pk and not self.qr_id:
            # Generate unique QR ID
            self.qr_id = generate_unique_qr_id()
            
            # Ensure uniqueness (avoid djongo issues)
            max_attempts = 10
            attempts = 0
            while attempts < max_attempts:
                try:
                    existing_user = User.objects.filter(qr_id=self.qr_id).first()
                    if not existing_user:
                        break
                    self.qr_id = generate_unique_qr_id()
                    attempts += 1
                except Exception as e:
                    logger.warning(f"QR ID uniqueness check failed (attempt {attempts}): {e}")
                    break
            
            logger.info(f"Generated QR ID for new user: {self.qr_id}")
        
        # Save the user first to get an ID
        super().save(*args, **kwargs)
        
        # Generate QR code if it doesn't exist
        if not self.qr_image:
            try:
                file_path, file_content = generate_qr_code(self.qr_id, self.name)
                self.qr_image = file_path

                # Save the QR code file using default storage
                from django.core.files.storage import default_storage
                saved_path = default_storage.save(file_path, file_content)

                # Force save the qr_image field to database
                super().save(update_fields=['qr_image'])

                logger.info(f"Generated QR code for user {self.email}: {saved_path}")
            except Exception as e:
                logger.error(f"Error generating QR code for user {self.email}: {e}")
                # Set a fallback text file
                self.qr_image = f"qr_codes/{self.qr_id}.txt"

        # Always save to ensure all changes are persisted
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Override delete method to remove QR code image when user is deleted.
        """
        # Delete QR code image
        if self.qr_id:
            try:
                delete_qr_code(self.qr_id)
                logger.info(f"Deleted QR code for user {self.email}")
            except Exception as e:
                logger.error(f"Error deleting QR code for user {self.email}: {e}")
        
        # Call parent delete
        super().delete(*args, **kwargs)
    
    def get_qr_image_url(self, request=None):
        """
        Get the full URL for the user's QR code image.
        
        Args:
            request: Django request object for building absolute URL
            
        Returns:
            str: Full URL to the QR code image, or None if not available
        """
        if not self.qr_image:
            return None
        
        from django.conf import settings
        
        if request:
            return request.build_absolute_uri(f"{settings.MEDIA_URL}{self.qr_image}")
        else:
            # Fallback URL without request
            return f"{settings.MEDIA_URL}{self.qr_image}"
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin' or self.is_superuser
    
    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        return True if self.is_superuser else False
    
    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        return True if self.is_superuser else False
