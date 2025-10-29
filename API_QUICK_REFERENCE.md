# 🚀 API Quick Reference

## 📍 Swagger URLs

| Interface | URL | Purpose |
|-----------|-----|---------|
| **Swagger UI** | http://localhost:8000/api/docs/ | Interactive API testing |
| **ReDoc** | http://localhost:8000/api/redoc/ | Clean documentation view |
| **OpenAPI Schema** | http://localhost:8000/api/schema/ | Raw API specification |

---

## 🔐 Authentication Endpoints

### Register User
```bash
POST /api/register/

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "role": "user"  # Optional: "user" or "admin"
}
```

### Login
```bash
POST /api/login/

{
  "email": "john@example.com",
  "password": "securepass123"
}
```

### Logout
```bash
POST /api/logout/
Authorization: Bearer {access_token}

{
  "refresh": "{refresh_token}"
}
```

---

## 👥 User Management Endpoints

### Get All Users
```bash
GET /api/users/
Authorization: Bearer {access_token}
```

### Get Current User
```bash
GET /api/me/
Authorization: Bearer {access_token}
```

### Get User by ID
```bash
GET /api/users/{id}/
Authorization: Bearer {access_token}
```

### Delete User
```bash
DELETE /api/users/{id}/delete/
Authorization: Bearer {access_token}
```

---

## 🎫 QR Verification

### Verify QR Code
```bash
GET /api/verify/{qr_id}/
# No authentication required
```

**Example:**
```bash
GET /api/verify/QR-A1B2C3D4/
```

---

## 🧪 Quick Test with cURL

### 1. Register
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123",
    "password_confirm": "test123",
    "role": "user"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

### 3. Get Current User
```bash
curl -X GET http://localhost:8000/api/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Verify QR Code
```bash
curl -X GET http://localhost:8000/api/verify/QR-A1B2C3D4/
```

---

## 🐍 Python Examples

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Register
r = requests.post(f"{BASE_URL}/register/", json={
    "name": "Python User",
    "email": "python@example.com",
    "password": "pass123",
    "password_confirm": "pass123"
})
tokens = r.json()['tokens']

# Get current user
headers = {"Authorization": f"Bearer {tokens['access']}"}
me = requests.get(f"{BASE_URL}/me/", headers=headers)
print(me.json())

# Verify QR
qr_id = r.json()['user']['qr_id']
verify = requests.get(f"{BASE_URL}/verify/{qr_id}/")
print(verify.json())
```

---

## 🌐 JavaScript/Fetch Examples

```javascript
const BASE_URL = 'http://localhost:8000/api';

// Register
const register = await fetch(`${BASE_URL}/register/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'JS User',
    email: 'js@example.com',
    password: 'pass123',
    password_confirm: 'pass123'
  })
});
const { tokens, user } = await register.json();

// Get current user
const me = await fetch(`${BASE_URL}/me/`, {
  headers: { 'Authorization': `Bearer ${tokens.access}` }
});
console.log(await me.json());

// Verify QR
const verify = await fetch(`${BASE_URL}/verify/${user.qr_id}/`);
console.log(await verify.json());
```

---

## 📊 Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 205 | Reset Content - Logout successful |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 405 | Method Not Allowed - Wrong HTTP method |

---

## 🔑 JWT Token Usage

### Access Token
- **Lifetime:** 60 minutes (default)
- **Use:** Include in Authorization header
- **Format:** `Authorization: Bearer {access_token}`

### Refresh Token
- **Lifetime:** 24 hours (default)
- **Use:** Get new access token or logout
- **Format:** Send in request body

---

## 🎯 Common Workflows

### Workflow 1: User Registration & Login
```
1. POST /api/register/      → Get tokens & QR ID
2. Save access_token
3. Use token for authenticated requests
```

### Workflow 2: QR Verification
```
1. Scan QR code → Get QR ID
2. GET /api/verify/{qr_id}/ → Verify user
3. Grant/Deny access based on response
```

### Workflow 3: Token Refresh
```
1. Access token expires
2. POST /api/token/refresh/ with refresh token
3. Get new access token
4. Continue using API
```

---

## 🛡️ Role-Based Access

### User Roles
- **user** (default): Standard user access
- **admin**: Full system access

### Creating Admin User
```json
{
  "name": "Admin User",
  "email": "admin@example.com",
  "password": "adminpass123",
  "password_confirm": "adminpass123",
  "role": "admin"
}
```

---

## 🐛 Troubleshooting

### Error: "Unauthorized"
➡️ Add Authorization header with Bearer token

### Error: "Token expired"
➡️ Login again to get new tokens

### Error: "User not found"
➡️ Check QR ID is correct and user is active

### Error: "Validation error"
➡️ Check request body matches required format

---

## 📱 Postman Collection

Import the Postman collection:
```
File: QR_Access_API.postman_collection.json
```

Or use Swagger's "Download" button to export OpenAPI spec for Postman.

---

## 🔗 Quick Links

- **Swagger UI**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/
- **Full Documentation**: See `SWAGGER_GUIDE.md`
- **API Docs**: See `API_DOCUMENTATION.md`

---

## 💡 Pro Tips

1. **Use Swagger UI** for quick testing - it's the fastest way
2. **Save your tokens** - you'll need them for multiple requests
3. **Check role field** - different roles have different permissions
4. **QR verification needs no auth** - perfect for Raspberry Pi
5. **Tokens expire** - re-login when they do

---

**Start testing:** http://localhost:8000/api/docs/
