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

### 9. Create Team

**Endpoint:** `POST /api/teams/`

**Authentication:** Required (Bearer token)

**Description:** Create a new team for the authenticated user.

**Request Body:**
```json
{
  "team_name": "string (required)"
}
```

**Success Response (201 Created):**
```json
{
  "team_id": "TEAM-XXXXXXXX",
  "team_name": "string",
  "user": "user_id",
  "user_name": "string",
  "total_games": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "is_active": true
}
```

**Error Responses:**
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl -X POST http://localhost:8000/api/teams/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "team_name": "Warriors"
  }'
```

---

### 10. List User Teams

**Endpoint:** `GET /api/teams/`

**Authentication:** Required (Bearer token)

**Description:** Get all teams created by the authenticated user.

**Success Response (200 OK):**
```json
{
  "teams": [
    {
      "team_id": "TEAM-XXXXXXXX",
      "team_name": "string",
      "user": "user_id",
      "user_name": "string",
      "total_games": 5,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "is_active": true
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl http://localhost:8000/api/teams/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 11. Get Team Details

**Endpoint:** `GET /api/teams/<team_id>/`

**Authentication:** Required (Bearer token)

**Description:** Get detailed team information including all game results.

**URL Parameters:**
- `team_id` (string) - Team ID (e.g., TEAM-XXXXXXXX)

**Success Response (200 OK):**
```json
{
  "team_id": "TEAM-XXXXXXXX",
  "team_name": "string",
  "user": "user_id",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "is_active": true,
  "game_results": [
    {
      "result_id": "RESULT-XXXXXXXX",
      "user": "user_id",
      "user_name": "string",
      "team": "team_id",
      "team_name": "string",
      "game": "game_id",
      "game_name": "string",
      "points_scored": 100,
      "played_at": "2024-01-01T00:00:00Z",
      "notes": "string",
      "verified_by_admin": false,
      "admin_user": null,
      "admin_name": null
    }
  ],
  "total_points": 100
}
```

**Error Responses:**
- `404 Not Found` - Team not found or not owned by user
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl http://localhost:8000/api/teams/TEAM-XXXXXXXX/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 12. Update Team

**Endpoint:** `PUT /api/teams/<team_id>/`

**Authentication:** Required (Bearer token)

**Description:** Update team information.

**URL Parameters:**
- `team_id` (string) - Team ID

**Request Body:**
```json
{
  "team_name": "string (optional)"
}
```

**Success Response (200 OK):**
```json
{
  "team_id": "TEAM-XXXXXXXX",
  "team_name": "Updated Name",
  "user": "user_id",
  "user_name": "string",
  "total_games": 5,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "is_active": true
}
```

**Error Responses:**
- `404 Not Found` - Team not found
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl -X PUT http://localhost:8000/api/teams/TEAM-XXXXXXXX/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "team_name": "Updated Warriors"
  }'
```

---

### 13. Delete Team

**Endpoint:** `DELETE /api/teams/<team_id>/`

**Authentication:** Required (Bearer token)

**Description:** Soft delete a team (sets is_active to false).

**URL Parameters:**
- `team_id` (string) - Team ID

**Success Response (200 OK):**
```json
{
  "message": "Team deleted successfully"
}
```

**Error Responses:**
- `404 Not Found` - Team not found
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/teams/TEAM-XXXXXXXX/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 14. List All Games

**Endpoint:** `GET /api/games/`

**Authentication:** Required (Bearer token)

**Description:** Get all active games available in the system.

**Success Response (200 OK):**
```json
{
  "games": [
    {
      "game_id": "GAME-XXXXXXXX",
      "game_name": "Basketball",
      "game_description": "Street basketball game",
      "max_points": 100,
      "min_points": 0,
      "is_active": true,
      "total_plays": 25,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl http://localhost:8000/api/games/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 15. Create Game Result

**Endpoint:** `POST /api/results/`

**Authentication:** Required (Bearer token)

**Description:** Record a game result for the authenticated user.

**Request Body:**
```json
{
  "team": "TEAM-XXXXXXXX (required)",
  "game": "GAME-XXXXXXXX (required)",
  "points_scored": 100,
  "notes": "string (optional)"
}
```

**Success Response (201 Created):**
```json
{
  "result_id": "RESULT-XXXXXXXX",
  "user": "user_id",
  "user_name": "string",
  "team": "team_id",
  "team_name": "string",
  "game": "game_id",
  "game_name": "string",
  "points_scored": 100,
  "played_at": "2024-01-01T00:00:00Z",
  "notes": "string",
  "verified_by_admin": false,
  "admin_user": null,
  "admin_name": null
}
```

**Error Responses:**
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl -X POST http://localhost:8000/api/results/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "team": "TEAM-XXXXXXXX",
    "game": "GAME-XXXXXXXX",
    "points_scored": 85,
    "notes": "Great performance!"
  }'
```

---

### 16. List User Game Results

**Endpoint:** `GET /api/results/`

**Authentication:** Required (Bearer token)

**Description:** Get all game results for the authenticated user.

**Success Response (200 OK):**
```json
{
  "results": [
    {
      "result_id": "RESULT-XXXXXXXX",
      "user": "user_id",
      "user_name": "string",
      "team": "team_id",
      "team_name": "string",
      "game": "game_id",
      "game_name": "string",
      "points_scored": 100,
      "played_at": "2024-01-01T00:00:00Z",
      "notes": "string",
      "verified_by_admin": false,
      "admin_user": null,
      "admin_name": null
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl http://localhost:8000/api/results/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Admin Endpoints

### 17. Create Game (Admin Only)

**Endpoint:** `POST /api/admin/games/`

**Authentication:** Required (Admin Bearer token)

**Description:** Create a new game in the system (admin only).

**Request Body:**
```json
{
  "game_name": "string (required)",
  "game_description": "string (optional)",
  "max_points": 100,
  "min_points": 0
}
```

**Success Response (201 Created):**
```json
{
  "game_id": "GAME-XXXXXXXX",
  "game_name": "Basketball",
  "game_description": "Street basketball game",
  "max_points": 100,
  "min_points": 0,
  "is_active": true,
  "total_plays": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `403 Forbidden` - Admin access required
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing or invalid access token

**Example:**
```bash
curl -X POST http://localhost:8000/api/admin/games/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_access_token>" \
  -d '{
    "game_name": "Soccer",
    "game_description": "5v5 soccer match",
    "max_points": 50,
    "min_points": 0
  }'
```

---

### 18. Update Game (Admin Only)

**Endpoint:** `PUT /api/admin/games/<game_id>/`

**Authentication:** Required (Admin Bearer token)

**Description:** Update game information (admin only).

**URL Parameters:**
- `game_id` (string) - Game ID

**Request Body:**
```json
{
  "game_name": "string (optional)",
  "game_description": "string (optional)",
  "max_points": 100,
  "min_points": 0,
  "is_active": true
}
```

**Success Response (200 OK):**
```json
{
  "game_id": "GAME-XXXXXXXX",
  "game_name": "Updated Name",
  "game_description": "Updated description",
  "max_points": 100,
  "min_points": 0,
  "is_active": true,
  "total_plays": 25,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `403 Forbidden` - Admin access required
- `404 Not Found` - Game not found
- `400 Bad Request` - Validation error

**Example:**
```bash
curl -X PUT http://localhost:8000/api/admin/games/GAME-XXXXXXXX/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_access_token>" \
  -d '{
    "game_name": "Updated Soccer",
    "is_active": false
  }'
```

---

### 19. List All Results (Admin Only)

**Endpoint:** `GET /api/admin/results/`

**Authentication:** Required (Admin Bearer token)

**Description:** Get all game results with optional filtering (admin only).

**Query Parameters:**
- `user_id` (string, optional) - Filter by user ID or email
- `team_id` (string, optional) - Filter by team ID
- `game_id` (string, optional) - Filter by game ID

**Success Response (200 OK):**
```json
{
  "results": [
    {
      "result_id": "RESULT-XXXXXXXX",
      "user": "user_id",
      "user_name": "string",
      "team": "team_id",
      "team_name": "string",
      "game": "game_id",
      "game_name": "string",
      "points_scored": 100,
      "played_at": "2024-01-01T00:00:00Z",
      "notes": "string",
      "verified_by_admin": true,
      "admin_user": "admin_user_id",
      "admin_name": "Admin Name"
    }
  ],
  "count": 1
}
```

**Error Responses:**
- `403 Forbidden` - Admin access required

**Examples:**
```bash
# Get all results
curl http://localhost:8000/api/admin/results/ \
  -H "Authorization: Bearer <admin_access_token>"

# Filter by user
curl "http://localhost:8000/api/admin/results/?user_id=user@example.com" \
  -H "Authorization: Bearer <admin_access_token>"

# Filter by team
curl "http://localhost:8000/api/admin/results/?team_id=TEAM-XXXXXXXX" \
  -H "Authorization: Bearer <admin_access_token>"

# Filter by game
curl "http://localhost:8000/api/admin/results/?game_id=GAME-XXXXXXXX" \
  -H "Authorization: Bearer <admin_access_token>"
```

---

### 20. Update Game Result (Admin Only)

**Endpoint:** `PUT /api/admin/results/<result_id>/`

**Authentication:** Required (Admin Bearer token)

**Description:** Update and verify a game result (admin only).

**URL Parameters:**
- `result_id` (string) - Result ID

**Request Body:**
```json
{
  "points_scored": 100,
  "notes": "string (optional)"
}
```

**Success Response (200 OK):**
```json
{
  "result_id": "RESULT-XXXXXXXX",
  "user": "user_id",
  "user_name": "string",
  "team": "team_id",
  "team_name": "string",
  "game": "game_id",
  "game_name": "string",
  "points_scored": 100,
  "played_at": "2024-01-01T00:00:00Z",
  "notes": "Verified by admin",
  "verified_by_admin": true,
  "admin_user": "admin_user_id",
  "admin_name": "Admin Name"
}
```

**Error Responses:**
- `403 Forbidden` - Admin access required
- `404 Not Found` - Result not found
- `400 Bad Request` - Validation error

**Example:**
```bash
curl -X PUT http://localhost:8000/api/admin/results/RESULT-XXXXXXXX/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_access_token>" \
  -d '{
    "points_scored": 95,
    "notes": "Adjusted after review"
  }'
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
