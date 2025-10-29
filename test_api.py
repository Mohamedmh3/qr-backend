"""
Simple API testing script for the QR Access Verification System.
Run this after starting the Django server to test all endpoints.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def test_register():
    """Test user registration."""
    print_info("Testing User Registration...")
    
    data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=data)
        
        if response.status_code == 201:
            result = response.json()
            print_success("User registered successfully!")
            print(f"  - Name: {result['user']['name']}")
            print(f"  - Email: {result['user']['email']}")
            print(f"  - QR ID: {result['user']['qr_id']}")
            print(f"  - QR Image: {result['user']['qr_image_url']}")
            return result
        else:
            print_error(f"Registration failed: {response.json()}")
            return None
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None


def test_login(email, password):
    """Test user login."""
    print_info("Testing User Login...")
    
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print_success("Login successful!")
            print(f"  - Access Token: {result['tokens']['access'][:50]}...")
            return result
        else:
            print_error(f"Login failed: {response.json()}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None


def test_verify_qr(qr_id):
    """Test QR code verification."""
    print_info(f"Testing QR Verification for: {qr_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/verify/{qr_id}/")
        
        if response.status_code == 200:
            result = response.json()
            print_success("QR verification successful!")
            print(f"  - Status: {result['status']}")
            print(f"  - Name: {result['name']}")
            print(f"  - Email: {result['email']}")
            return result
        else:
            print_error(f"QR verification failed: {response.json()}")
            return None
    except Exception as e:
        print_error(f"QR verification error: {str(e)}")
        return None


def test_get_users(access_token):
    """Test getting all users."""
    print_info("Testing Get All Users...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Retrieved {result['count']} user(s)")
            for user in result['users']:
                print(f"  - {user['name']} ({user['email']}) - QR: {user['qr_id']}")
            return result
        else:
            print_error(f"Get users failed: {response.json()}")
            return None
    except Exception as e:
        print_error(f"Get users error: {str(e)}")
        return None


def test_get_current_user(access_token):
    """Test getting current user."""
    print_info("Testing Get Current User...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/me/", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print_success("Current user retrieved!")
            print(f"  - Name: {result['name']}")
            print(f"  - Email: {result['email']}")
            return result
        else:
            print_error(f"Get current user failed: {response.json()}")
            return None
    except Exception as e:
        print_error(f"Get current user error: {str(e)}")
        return None


def test_logout(access_token, refresh_token):
    """Test user logout."""
    print_info("Testing User Logout...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/logout/", json=data, headers=headers)
        
        if response.status_code == 205:
            print_success("Logout successful!")
            return True
        else:
            print_error(f"Logout failed: {response.json()}")
            return False
    except Exception as e:
        print_error(f"Logout error: {str(e)}")
        return False


def main():
    """Run all API tests."""
    print("\n" + "="*60)
    print("  QR Access Verification System - API Tests")
    print("="*60 + "\n")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL.replace('/api', '/'))
        print_success("Server is running!")
    except:
        print_error("Server is not running. Please start it with: python manage.py runserver")
        sys.exit(1)
    
    print("\n" + "-"*60 + "\n")
    
    # Test 1: Register
    register_result = test_register()
    if not register_result:
        print_warning("Skipping remaining tests due to registration failure")
        return
    
    qr_id = register_result['user']['qr_id']
    email = register_result['user']['email']
    
    print("\n" + "-"*60 + "\n")
    
    # Test 2: Login
    login_result = test_login(email, "testpass123")
    if not login_result:
        print_warning("Skipping remaining tests due to login failure")
        return
    
    access_token = login_result['tokens']['access']
    refresh_token = login_result['tokens']['refresh']
    
    print("\n" + "-"*60 + "\n")
    
    # Test 3: Verify QR
    test_verify_qr(qr_id)
    
    print("\n" + "-"*60 + "\n")
    
    # Test 4: Get all users
    test_get_users(access_token)
    
    print("\n" + "-"*60 + "\n")
    
    # Test 5: Get current user
    test_get_current_user(access_token)
    
    print("\n" + "-"*60 + "\n")
    
    # Test 6: Logout
    test_logout(access_token, refresh_token)
    
    print("\n" + "="*60)
    print("  All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
