# API Documentation - QR Access Verification System

## Base URL
```
http://localhost:8000/api
```

---

## Authentication

Most endpoints require JWT authentication. Include the access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. User Registration

**Endpoint:** `POST /api/register/`

**Authentication:** Not required

**Description:** Register a new user and generate their unique QR code.

**Request Body:**
```json
{
  "name": "string (required)",
  "email": "string (required, must be valid email)",
  "password": "string (required, min 8 characters)",
  "password_confirm": "string (required, must match password)"
}
```

**Success Response (201 Created):**
```json
{
  "user": {
    "id": "string",
    "name": "string",
    "email": "string",
    "qr_id": "string (format: QR-XXXXXXXX)",
    "qr_image_url": "string (full URL to QR code image)"
  },
  "tokens": {
    "refresh": "string (JWT refresh token)",
    "access": "string (JWT access token)"
  },
  "message": "User registered successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Validation error (passwords don't match, email already exists, etc.)

**Example:**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

---

### 2. User Login

**Endpoint:** `POST /api/login/`

**Authentication:** Not required

**Description:** Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "user": {
    "id": "string",
    "name": "string",
    "email": "string",
    "qr_id": "string",
    "qr_image_url": "string"
  },
  "tokens": {
    "refresh": "string",
    "access": "string"
  },
  "message": "Login successful"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid credentials
- `400 Bad Request` - User account is disabled

**Example:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

---

### 3. User Logout

**Endpoint:** `POST /api/logout/`

**Authentication:** Required (Bearer token)

**Description:** Logout user by blacklisting their refresh token.

**Request Body:**
```json
{
  "refresh": "string (required, refresh token from login)"
}
```

**Success Response (205 Reset Content):**
```json
{
  "message": "Logout successful"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid token or token already blacklisted
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl -X POST http://localhost:8000/api/logout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "refresh": "<refresh_token>"
  }'
```

---

### 4. Verify QR Code

**Endpoint:** `GET /api/verify/<qr_id>/`

**Authentication:** Not required

**Description:** Verify a QR code and return user information. Used by Raspberry Pi for access control.

**URL Parameters:**
- `qr_id` (string) - The QR ID to verify (e.g., QR-A1B2C3D4)

**Success Response (200 OK):**
```json
{
  "status": "success",
  "name": "string",
  "email": "string",
  "qr_id": "string",
  "message": "User verified successfully"
}
```

**Error Response (404 Not Found):**
```json
{
  "status": "failure",
  "message": "User not found or inactive"
}
```

**Example:**
```bash
curl http://localhost:8000/api/verify/QR-A1B2C3D4/
```

**Use Case - Raspberry Pi:**
```python
import requests

def verify_access(qr_id):
    response = requests.get(f'http://localhost:8000/api/verify/{qr_id}/')
    data = response.json()
    
    if response.status_code == 200 and data['status'] == 'success':
        print(f"Access granted for: {data['name']}")
        # Trigger door unlock, etc.
        return True
    else:
        print("Access denied")
        return False
```

---

### 5. List All Users

**Endpoint:** `GET /api/users/`

**Authentication:** Required (Bearer token)

**Description:** Get a list of all registered users.

**Success Response (200 OK):**
```json
{
  "count": 10,
  "users": [
    {
      "id": "string",
      "name": "string",
      "email": "string",
      "qr_id": "string",
      "qr_image_url": "string",
      "is_active": true,
      "is_staff": false,
      "date_joined": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl http://localhost:8000/api/users/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 6. Get User Details

**Endpoint:** `GET /api/users/<id>/`

**Authentication:** Required (Bearer token)

**Description:** Get detailed information about a specific user.

**URL Parameters:**
- `id` (string) - User ID

**Success Response (200 OK):**
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "qr_id": "string",
  "qr_image_url": "string",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `404 Not Found` - User not found
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl http://localhost:8000/api/users/<user_id>/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 7. Delete User

**Endpoint:** `DELETE /api/users/<id>/delete/`

**Authentication:** Required (Bearer token)

**Description:** Delete a user and their associated QR code.

**URL Parameters:**
- `id` (string) - User ID to delete

**Success Response (200 OK):**
```json
{
  "message": "User john@example.com deleted successfully"
}
```

**Error Responses:**
- `404 Not Found` - User not found
- `403 Forbidden` - Cannot delete your own account
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/users/<user_id>/delete/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 8. Get Current User

**Endpoint:** `GET /api/me/`

**Authentication:** Required (Bearer token)

**Description:** Get information about the currently authenticated user.

**Success Response (200 OK):**
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "qr_id": "string",
  "qr_image_url": "string",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl http://localhost:8000/api/me/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 205 | Reset Content - Logout successful |
| 400 | Bad Request - Validation error |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message",
  "field_name": ["Field-specific error message"]
}
```

Examples:

```json
{
  "email": ["A user with this email already exists."],
  "password": ["Password fields didn't match."]
}
```

```json
{
  "detail": "Invalid email or password."
}
```

---

## JWT Token Information

### Token Lifetimes
- **Access Token**: 60 minutes (configurable)
- **Refresh Token**: 24 hours (configurable)

### Token Refresh

To refresh an expired access token, use the refresh token to get a new pair:

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>"
  }'
```

**Note:** This endpoint is provided by Django Simple JWT and is automatically available.

---

## Rate Limiting

Currently, there are no rate limits enforced. In production, consider implementing rate limiting using:
- Django Ratelimit
- DRF Throttling
- Nginx rate limiting

---

## CORS

The API is configured to accept requests from:
- `http://localhost:3000` (Flutter/Mobile)
- `http://localhost:5173` (React/Web)

To add more origins, update the `CORS_ALLOWED_ORIGINS` in `.env`.

---

## Media Files

QR code images are served from:
```
http://localhost:8000/media/qr_codes/<QR_ID>.png
```

Example:
```
http://localhost:8000/media/qr_codes/QR-A1B2C3D4.png
```

---

## Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (never in localStorage for web apps if possible)
3. **Refresh tokens before they expire**
4. **Implement proper error handling**
5. **Validate all user input**
6. **Use environment variables for sensitive data**

---

## Support

For issues or questions, refer to:
- Main README.md
- SETUP_GUIDE.md
- Django REST Framework documentation
