# 📚 Swagger API Documentation Guide

## 🚀 Access Swagger UI

Your API documentation is now available at:

### **Swagger UI (Interactive)**
```
http://localhost:8000/api/docs/
```
👉 **Best for testing** - Try out APIs directly in your browser!

### **ReDoc (Read-only)**
```
http://localhost:8000/api/redoc/
```
👉 **Best for reading** - Clean, organized documentation view

### **OpenAPI Schema (JSON)**
```
http://localhost:8000/api/schema/
```
👉 **For developers** - Raw OpenAPI specification

---

## 📖 How to Use Swagger UI

### Step 1: Open Swagger UI
1. Make sure your server is running: `python manage.py runserver 8000`
2. Open browser: http://localhost:8000/api/docs/
3. You'll see all API endpoints organized by tags

---

## 🔐 Testing Authentication Endpoints

### 1️⃣ **Register a New User**

**Endpoint:** `POST /api/register/`

1. Click on **"POST /api/register/"** to expand it
2. Click **"Try it out"** button
3. Edit the request body:
   ```json
   {
     "name": "Test User",
     "email": "test@example.com",
     "password": "testpass123",
     "password_confirm": "testpass123",
     "role": "user"
   }
   ```
4. Click **"Execute"**
5. Check the response - you'll get:
   - User data with `qr_id`
   - JWT tokens (`access` and `refresh`)

**Response Example:**
```json
{
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "Test User",
    "email": "test@example.com",
    "role": "user",
    "qr_id": "QR-A1B2C3D4",
    "qr_image_url": "http://localhost:8000/media/qr_codes/QR-A1B2C3D4.txt"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "User registered successfully"
}
```

📋 **Copy the `access` token** - you'll need it for authenticated endpoints!

---

### 2️⃣ **Login**

**Endpoint:** `POST /api/login/`

1. Click on **"POST /api/login/"**
2. Click **"Try it out"**
3. Enter credentials:
   ```json
   {
     "email": "test@example.com",
     "password": "testpass123"
   }
   ```
4. Click **"Execute"**
5. Copy the `access` token from the response

---

### 3️⃣ **Authenticate for Protected Endpoints**

After getting your access token, you need to authorize Swagger:

1. **Scroll to the top** of Swagger UI
2. Click the **"Authorize" button** (🔒 icon)
3. In the popup, enter your token:
   ```
   Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   ```
   ⚠️ **Important:** Include the word "Bearer" followed by a space, then your token
4. Click **"Authorize"**
5. Click **"Close"**

✅ Now you can access all protected endpoints!

---

## 🎯 Testing QR Verification

### **Verify QR Code**

**Endpoint:** `GET /api/verify/{qr_id}/`

This endpoint **doesn't require authentication** (used by Raspberry Pi).

1. Click on **"GET /api/verify/{qr_id}/"**
2. Click **"Try it out"**
3. Enter a QR ID in the `qr_id` parameter (e.g., `QR-A1B2C3D4`)
4. Click **"Execute"**

**Success Response:**
```json
{
  "status": "success",
  "name": "Test User",
  "email": "test@example.com",
  "role": "user",
  "qr_id": "QR-A1B2C3D4",
  "message": "User verified successfully"
}
```

**Error Response:**
```json
{
  "status": "failure",
  "message": "User not found or inactive"
}
```

---

## 👥 Testing User Management Endpoints

These endpoints **require authentication**. Make sure you've authorized using the "Authorize" button!

### **Get All Users**

**Endpoint:** `GET /api/users/`

1. Click **"Authorize"** and add your token if you haven't
2. Click on **"GET /api/users/"**
3. Click **"Try it out"**
4. Click **"Execute"**

**Response:**
```json
{
  "count": 1,
  "users": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Test User",
      "email": "test@example.com",
      "role": "user",
      "qr_id": "QR-A1B2C3D4",
      "qr_image_url": "...",
      "is_active": true,
      "is_staff": false,
      "date_joined": "2024-10-24T12:00:00Z",
      "last_login": "2024-10-24T12:00:00Z"
    }
  ]
}
```

### **Get Current User (Me)**

**Endpoint:** `GET /api/me/`

1. Click on **"GET /api/me/"**
2. Click **"Try it out"**
3. Click **"Execute"**

Returns your own user profile.

### **Get User by ID**

**Endpoint:** `GET /api/users/{id}/`

1. Click on **"GET /api/users/{id}/"**
2. Click **"Try it out"**
3. Enter a user ID in the `id` parameter
4. Click **"Execute"**

---

## 🚪 Testing Logout

**Endpoint:** `POST /api/logout/`

1. Make sure you're authenticated
2. Click on **"POST /api/logout/"**
3. Click **"Try it out"**
4. Enter your refresh token:
   ```json
   {
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
   }
   ```
5. Click **"Execute"**

**Response:**
```json
{
  "message": "Logout successful"
}
```

---

## 🎨 Swagger UI Features

### **Try It Out**
- Execute API calls directly from the browser
- See real-time responses
- Test with different parameters

### **Schemas**
- Click "Schemas" at the bottom to see all data models
- Understand request/response structure

### **Authorization**
- Lock icon 🔒 shows protected endpoints
- Green lock means you're authorized
- Red lock means you need to authorize

### **Response Codes**
- **200**: Success
- **201**: Created successfully
- **400**: Bad request (validation error)
- **401**: Unauthorized (need to login)
- **404**: Not found
- **405**: Method not allowed

---

## 🔧 Common Issues & Solutions

### Issue 1: "Unauthorized" Error
**Solution:** Click "Authorize" and add your token with "Bearer " prefix

### Issue 2: Token Expired
**Solution:** Login again to get a new token

### Issue 3: "Method Not Allowed"
**Solution:** Make sure you're using the correct HTTP method (GET/POST/etc.)

### Issue 4: Can't See Swagger UI
**Solution:** 
- Make sure server is running: `python manage.py runserver 8000`
- Check URL: http://localhost:8000/api/docs/
- Clear browser cache

---

## 📝 Quick Testing Workflow

1. **Register** a new user → Get tokens
2. **Authorize** Swagger with the access token
3. **Test** protected endpoints (users list, me, etc.)
4. **Verify** QR code (no auth needed)
5. **Logout** when done

---

## 🎯 Testing Scenarios

### Scenario 1: Register → Login → View Profile
```
1. POST /api/register/ (create account)
2. POST /api/login/ (get fresh tokens)
3. Authorize with access token
4. GET /api/me/ (view your profile)
```

### Scenario 2: QR Code Verification Flow
```
1. POST /api/register/ (get qr_id from response)
2. GET /api/verify/{qr_id}/ (verify the QR code)
```

### Scenario 3: Admin User Management
```
1. POST /api/register/ with role="admin"
2. Authorize with admin token
3. GET /api/users/ (view all users)
4. GET /api/users/{id}/ (view specific user)
```

---

## 🚀 Advanced: Using Swagger with Code

### Python Example
```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Register
response = requests.post(f"{BASE_URL}/register/", json={
    "name": "API Test",
    "email": "api@example.com",
    "password": "test123",
    "password_confirm": "test123"
})
data = response.json()
access_token = data['tokens']['access']

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {access_token}"}
me = requests.get(f"{BASE_URL}/me/", headers=headers)
print(me.json())
```

### JavaScript/Fetch Example
```javascript
// Register
const registerResponse = await fetch('http://localhost:8000/api/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'JS Test',
    email: 'js@example.com',
    password: 'test123',
    password_confirm: 'test123'
  })
});
const { tokens } = await registerResponse.json();

// Use token
const meResponse = await fetch('http://localhost:8000/api/me/', {
  headers: { 'Authorization': `Bearer ${tokens.access}` }
});
const user = await meResponse.json();
console.log(user);
```

---

## 📚 Additional Resources

- **OpenAPI Specification**: http://localhost:8000/api/schema/
- **ReDoc Documentation**: http://localhost:8000/api/redoc/
- **Django Admin**: http://localhost:8000/admin/

---

## ✅ API Testing Checklist

- [ ] Register new user
- [ ] Login with credentials
- [ ] Authorize Swagger with token
- [ ] Get current user profile
- [ ] Get all users list
- [ ] Verify QR code
- [ ] Logout and blacklist token
- [ ] Try expired token (should fail)
- [ ] Register admin user
- [ ] Test role-based features

---

**Happy Testing! 🎉**

For issues or questions, check the main README.md or API_DOCUMENTATION.md files.
