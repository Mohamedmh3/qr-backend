"""
Test Vercel Deployment APIs
Tests all endpoints on the deployed Vercel backend
"""

import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "https://qr-backend-rho.vercel.app/api"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, details=""):
    """Print test result"""
    symbol = "✅" if status else "❌"
    color = Colors.GREEN if status else Colors.RED
    print(f"{symbol} {color}{name}{Colors.END}")
    if details:
        print(f"   {details}")

def print_section(title):
    """Print section header"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.END}\n")

# Global variables for storing test data
test_user_email = f"test_vercel_{datetime.now().timestamp()}@test.com"
test_user_password = "TestPassword123!"
access_token = None
user_id = None
team_id = None
game_id = None
result_id = None


def test_health_check():
    """Test health check endpoint"""
    print_section("1. HEALTH CHECK")
    
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_test("Health Check", True, f"Status: {data.get('status')}")
            return True
        else:
            print_test("Health Check", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False


def test_register():
    """Test user registration"""
    print_section("2. USER REGISTRATION")
    
    global user_id
    
    payload = {
        "name": "Test Vercel User",
        "email": test_user_email,
        "password": test_user_password,
        "password_confirm": test_user_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=payload, timeout=30)
        
        if response.status_code == 201:
            data = response.json()
            user_id = data['user']['id']
            print_test("User Registration", True, f"User ID: {user_id}")
            print(f"   QR ID: {data['user']['qr_id']}")
            return True
        else:
            print_test("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test("User Registration", False, f"Error: {str(e)}")
        return False


def test_login():
    """Test user login"""
    print_section("3. USER LOGIN")
    
    global access_token
    
    payload = {
        "email": test_user_email,
        "password": test_user_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data['access']
            print_test("User Login", True, f"Token received")
            print(f"   Access Token: {access_token[:50]}...")
            return True
        else:
            print_test("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test("User Login", False, f"Error: {str(e)}")
        return False


def test_current_user():
    """Test get current user"""
    print_section("4. GET CURRENT USER")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/me/", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_test("Get Current User", True, f"Name: {data['name']}")
            print(f"   Email: {data['email']}")
            print(f"   Role: {data['role']}")
            return True
        else:
            print_test("Get Current User", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Get Current User", False, f"Error: {str(e)}")
        return False


def test_list_users():
    """Test list all users"""
    print_section("5. LIST ALL USERS")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_test("List Users", True, f"Total users: {len(data)}")
            return True
        else:
            print_test("List Users", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("List Users", False, f"Error: {str(e)}")
        return False


def test_create_team():
    """Test create team"""
    print_section("6. CREATE TEAM")
    
    global team_id
    
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "team_name": f"Test Team {datetime.now().timestamp()}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/teams/", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 201:
            data = response.json()
            team_id = data['team_id']
            print_test("Create Team", True, f"Team ID: {team_id}")
            print(f"   Team Name: {data['team_name']}")
            return True
        else:
            print_test("Create Team", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test("Create Team", False, f"Error: {str(e)}")
        return False


def test_list_teams():
    """Test list teams"""
    print_section("7. LIST MY TEAMS")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/teams/", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_test("List Teams", True, f"Total teams: {len(data)}")
            return True
        else:
            print_test("List Teams", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("List Teams", False, f"Error: {str(e)}")
        return False


def test_list_games():
    """Test list games"""
    print_section("8. LIST GAMES")
    
    global game_id
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/games/", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                game_id = data[0]['game_id']
                print_test("List Games", True, f"Total games: {len(data)}")
                print(f"   First game: {data[0]['game_name']} (ID: {game_id})")
            else:
                print_test("List Games", True, "No games found (empty database)")
            return True
        else:
            print_test("List Games", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("List Games", False, f"Error: {str(e)}")
        return False


def test_create_result():
    """Test create game result"""
    print_section("9. CREATE GAME RESULT")
    
    global result_id
    
    if not game_id or not team_id:
        print_test("Create Game Result", False, "Skipped: No game or team available")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "team_id": team_id,
        "game_id": game_id,
        "points_scored": 85,
        "notes": "Test result from Vercel deployment"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/results/", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 201:
            data = response.json()
            result_id = data['result_id']
            print_test("Create Game Result", True, f"Result ID: {result_id}")
            print(f"   Points: {data['points_scored']}")
            return True
        else:
            print_test("Create Game Result", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test("Create Game Result", False, f"Error: {str(e)}")
        return False


def test_list_results():
    """Test list game results"""
    print_section("10. LIST GAME RESULTS")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/results/", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_test("List Results", True, f"Total results: {len(data)}")
            return True
        else:
            print_test("List Results", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("List Results", False, f"Error: {str(e)}")
        return False


def cleanup():
    """Clean up test data"""
    print_section("11. CLEANUP")
    
    # Note: In production, you might want to keep test data or delete via admin panel
    print_test("Cleanup", True, "Test data created (manual cleanup recommended)")


def main():
    """Run all tests"""
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("🧪 VERCEL DEPLOYMENT API TEST")
    print(f"{'='*60}{Colors.END}")
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test User: {test_user_email}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests in sequence
    results.append(("Health Check", test_health_check()))
    results.append(("User Registration", test_register()))
    results.append(("User Login", test_login()))
    
    if access_token:
        results.append(("Get Current User", test_current_user()))
        results.append(("List Users", test_list_users()))
        results.append(("Create Team", test_create_team()))
        results.append(("List Teams", test_list_teams()))
        results.append(("List Games", test_list_games()))
        results.append(("Create Game Result", test_create_result()))
        results.append(("List Results", test_list_results()))
    
    cleanup()
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All tests passed! Deployment is working perfectly!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  Some tests failed. Check the errors above.{Colors.END}")
    
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")


if __name__ == "__main__":
    main()
