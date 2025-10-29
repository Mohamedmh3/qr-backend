# Quick Setup Guide for QR Access Verification System

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### 2. Start MongoDB

```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 3. Setup Database

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Start Server

```bash
python manage.py runserver
```

✅ **Your API is now running at http://localhost:8000**

---

## 📋 Testing Checklist

### Test 1: Register a User

```bash
curl -X POST http://localhost:8000/api/register/ ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"John Doe\",\"email\":\"john@example.com\",\"password\":\"securepass123\",\"password_confirm\":\"securepass123\"}"
```

**Expected**: Status 201, returns user data with QR ID and tokens

### Test 2: Login

```bash
curl -X POST http://localhost:8000/api/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"john@example.com\",\"password\":\"securepass123\"}"
```

**Expected**: Status 200, returns user data and tokens

### Test 3: Verify QR Code

Replace `<QR_ID>` with the QR ID from registration:

```bash
curl http://localhost:8000/api/verify/<QR_ID>/
```

**Expected**: Status 200, returns user verification data

### Test 4: Get All Users (Authenticated)

Replace `<ACCESS_TOKEN>` with the token from login:

```bash
curl http://localhost:8000/api/users/ ^
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Expected**: Status 200, returns list of users

---

## 🔧 Common Issues & Solutions

### Issue: MongoDB Connection Error

**Solution:**
```bash
# Check if MongoDB is running
mongo --eval "db.version()"

# If not, start it
net start MongoDB  # Windows
sudo systemctl start mongod  # Linux
```

### Issue: Port 8000 Already in Use

**Solution:**
```bash
# Use a different port
python manage.py runserver 8080
```

### Issue: Module Import Errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: QR Code Images Not Showing

**Solution:**
- Check that `media/qr_codes/` directory exists
- Verify `MEDIA_ROOT` and `MEDIA_URL` in settings.py
- Ensure the server is serving media files (works automatically in DEBUG mode)

---

## 📱 Integration Examples

### Flutter Integration

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  
  Future<Map<String, dynamic>> register(String name, String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/register/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'email': email,
        'password': password,
        'password_confirm': password,
      }),
    );
    return jsonDecode(response.body);
  }
}
```

### React Integration

```javascript
const API_URL = 'http://localhost:8000/api';

export const registerUser = async (name, email, password) => {
  const response = await fetch(`${API_URL}/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name,
      email,
      password,
      password_confirm: password,
    }),
  });
  return response.json();
};
```

### Raspberry Pi Integration

```python
import requests

API_URL = 'http://localhost:8000/api'

def verify_qr(qr_id):
    """Verify QR code and grant/deny access."""
    response = requests.get(f'{API_URL}/verify/{qr_id}/')
    data = response.json()
    
    if data['status'] == 'success':
        print(f"✅ Access granted for: {data['name']}")
        return True
    else:
        print(f"❌ Access denied: {data['message']}")
        return False

# Usage
qr_id = input("Scan QR code: ")
verify_qr(qr_id)
```

---

## 🎯 Next Steps

1. ✅ Backend is running
2. 📱 Connect your Flutter app to `http://localhost:8000/api`
3. 🖥️ Connect your React dashboard to `http://localhost:8000/api`
4. 🔌 Connect your Raspberry Pi to the `/api/verify/` endpoint
5. 📊 Access admin panel at `http://localhost:8000/admin`

---

## 📞 API Endpoint Summary

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/register/` | POST | No | Register new user |
| `/api/login/` | POST | No | Login user |
| `/api/logout/` | POST | Yes | Logout user |
| `/api/verify/<qr_id>/` | GET | No | Verify QR code |
| `/api/users/` | GET | Yes | List all users |
| `/api/users/<id>/` | GET | Yes | Get user details |
| `/api/users/<id>/delete/` | DELETE | Yes | Delete user |
| `/api/me/` | GET | Yes | Get current user |

---

**Need help?** Check the main README.md for detailed documentation.
