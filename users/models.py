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
from bson import ObjectId
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
    
    # Primary key field - using CharField to store MongoDB ObjectId as string
    id = models.CharField(max_length=24, primary_key=True, editable=False)
    
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
        indexes = [
            models.Index(fields=['qr_id'], name='user_qr_id_idx'),
            models.Index(fields=['email'], name='user_email_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    # Removed custom id property to avoid interfering with Django PK handling
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate ID and QR ID on creation.
        """
        # Handle update_fields parameter for last_login updates
        if 'update_fields' in kwargs and 'last_login' in kwargs['update_fields']:
            # For last_login updates, just call parent save
            return super().save(*args, **kwargs)
        
        # Generate ID if this is a new user (MongoDB ObjectId as string)
        if not self.id:
            self.id = str(ObjectId())
            logger.info(f"Generated ID for new user: {self.id}")
        
        # Generate QR ID if this is a new user
        if not self.qr_id:
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
        
        # Save the user
        super().save(*args, **kwargs)

        # NOTE: Skip QR image generation here to avoid issues.
        # QR generation can be handled lazily via login or a separate endpoint.
        return
    
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


class Team(models.Model):
    """Team model for user-created teams"""
    team_id = models.CharField(max_length=20, unique=True, primary_key=True)
    team_name = models.CharField(max_length=255)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'teams'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Generate team_id if not set"""
        if not self.team_id:
            self.team_id = f"TEAM-{uuid.uuid4().hex[:8].upper()}"
            logger.info(f"Generated team_id: {self.team_id}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.team_name} (Owner: {self.user.name})"


class Game(models.Model):
    """Game model for available games"""
    game_id = models.CharField(max_length=20, unique=True, primary_key=True)
    game_name = models.CharField(max_length=255, unique=True)
    game_description = models.TextField(blank=True, null=True)
    max_points = models.IntegerField(default=100)
    min_points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'games'
        ordering = ['game_name']
    
    def save(self, *args, **kwargs):
        """Generate game_id if not set"""
        if not self.game_id:
            self.game_id = f"GAME-{uuid.uuid4().hex[:8].upper()}"
            logger.info(f"Generated game_id: {self.game_id}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.game_name


class GameResult(models.Model):
    """Game results linking users, teams, and games"""
    result_id = models.CharField(max_length=20, unique=True, primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='game_results')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='game_results')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='results')
    points_scored = models.IntegerField(default=0)
    played_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    verified_by_admin = models.BooleanField(default=False)
    admin_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_results')
    
    class Meta:
        db_table = 'game_results'
        ordering = ['-played_at']
    
    def save(self, *args, **kwargs):
        """Generate result_id and validate points"""
        if not self.result_id:
            self.result_id = f"RESULT-{uuid.uuid4().hex[:8].upper()}"
            logger.info(f"Generated result_id: {self.result_id}")
        
        # Validate points are within game limits
        if self.game:
            if self.points_scored < self.game.min_points or self.points_scored > self.game.max_points:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f"Points must be between {self.game.min_points} and {self.game.max_points}"
                )
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.name} - {self.team.team_name} - {self.game.game_name}: {self.points_scored} pts"
