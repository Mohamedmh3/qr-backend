"""
Test cases for the QR Access Verification System.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User


class UserRegistrationTestCase(APITestCase):
    """Test cases for user registration endpoint."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.register_url = reverse('users:register')
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertTrue(response.data['user']['qr_id'].startswith('QR-'))
    
    def test_user_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        }
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    """Test cases for user login endpoint."""
    
    def setUp(self):
        """Set up test user and client."""
        self.client = APIClient()
        self.login_url = reverse('users:login')
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
    
    def test_user_login_success(self):
        """Test successful user login."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class QRVerificationTestCase(APITestCase):
    """Test cases for QR verification endpoint."""
    
    def setUp(self):
        """Set up test user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
    
    def test_qr_verification_success(self):
        """Test successful QR verification."""
        url = reverse('users:verify', kwargs={'qr_id': self.user.qr_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['name'], 'Test User')
    
    def test_qr_verification_not_found(self):
        """Test QR verification with invalid QR ID."""
        url = reverse('users:verify', kwargs={'qr_id': 'QR-INVALID'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'failure')
