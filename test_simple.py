"""Simple test to check Vercel deployment"""
import requests

BASE_URL = "https://qr-backend-rho.vercel.app"

print("Testing Vercel Deployment...")
print(f"Base URL: {BASE_URL}\n")

# Test 1: Root endpoint
print("1. Testing root endpoint...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: API health endpoint
print("\n2. Testing /api/health/ endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/health/", timeout=30)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
    else:
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Admin endpoint
print("\n3. Testing /admin/ endpoint...")
try:
    response = requests.get(f"{BASE_URL}/admin/", timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   Response length: {len(response.text)} chars")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("Note: 500 errors usually mean:")
print("  - Missing environment variables in Vercel")
print("  - Database connection issues")
print("  - Missing dependencies")
print("="*60)
