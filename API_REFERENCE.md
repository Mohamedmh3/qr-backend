# Team Management & Gaming Platform API Reference

This document describes all available REST API endpoints, authentication, request/response formats, and examples. Base URL assumes a local server.

- Base URL: `http://localhost:8000`
- API Prefix: `/api`
- Auth: JWT Bearer tokens unless noted

---

## Table of Contents
- [Authentication](#authentication)
  - [Register](#register)
  - [Login](#login)
  - [Logout](#logout)
  - [Refresh Token](#refresh-token-optional)
- [Users](#users)
  - [Current User](#current-user)
  - [List All Users](#list-all-users-admin-or-auth)
- [QR Verification](#qr-verification)
- [Teams](#teams)
  - [Create Team](#create-team)
  - [List My Teams](#list-my-teams)
  - [Get Team Detail](#get-team-detail)
  - [Update Team](#update-team)
  - [Delete Team (Soft Delete)](#delete-team-soft-delete)
- [Games](#games)
  - [List Games](#list-games)
  - [Admin Create/Update Game](#admin-createupdate-game)
- [Results](#results)
  - [Create Result](#create-result)
  - [List My Results](#list-my-results)
- [Admin Results](#admin-results)
  - [List All Results (Admin)](#list-all-results-admin)
  - [Update Result (Admin)](#update-result-admin)
- [Common Errors](#common-errors)
- [Status Codes](#status-codes)

---

## Authentication

All protected endpoints require an `Authorization: Bearer <access_token>` header. Tokens are issued on registration/login.

### Register
- **POST** `/api/register/`
- Public

Request
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "role": "user"  
}
```

Response 201
```json
{
  "user": {    "id": "6905...",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "qr_id": "QR-AB12CD34",
    "qr_image_url": "/media/qr_codes/QR-AB12CD34.png"
  },
  "tokens": {
    "access": "<jwt>",
    "refresh": "<jwt>"
  },
  "message": "User registered successfully"
}
```

Example
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name":"John Doe",
    "email":"john@example.com",
    "password":"SecurePass123!",
    "password_confirm":"SecurePass123!"
  }'
```

### Login
- **POST** `/api/login/`
- Public

Request
```json
{ "email": "john@example.com", "password": "SecurePass123!" }
```

Response 200
```json
{
  "user": { "id": "...", "name": "John Doe", "email": "john@example.com", "role": "user", "qr_id": "QR-...", "qr_image_url": "..." },
  "tokens": { "access": "<jwt>", "refresh": "<jwt>" },
  "message": "Login successful"
}
```

### Logout
- **POST** `/api/logout/`
- Auth required
- Invalidates refresh token if provided (implementation dependent)

Request
```json
{ "refresh": "<refresh_token>" }
```

Response 200
```json
{ "message": "Logged out successfully" }
```

### Refresh Token (optional)
- If enabled in your setup
- **POST** `/api/token/refresh/`

Request
```json
{ "refresh": "<refresh_token>" }
```

Response 200
```json
{ "access": "<new_access_token>" }
```

---

## Users

### Current User
- **GET** `/api/me/`
- Auth required

Response 200
```json
{ "id":"...","name":"John","email":"john@example.com","role":"user","qr_id":"QR-...","qr_image_url":"...","is_active":true,"date_joined":"...","last_login":null }
```

### List All Users (Admin or Auth)
- **GET** `/api/users/`
- Auth required (in this build returns basic list for authenticated users)

Response 200
```json
{ "users": [{"id":"...","name":"...","email":"...","role":"user"}], "count": 24 }
```

---

## QR Verification

### Verify QR by QR ID
- **GET** `/api/verify/<qr_id>/`
- Public (no auth)

Response 200
```json
{ "status": "success", "name":"John Doe", "email":"john@example.com", "role":"user", "qr_id":"QR-AB12CD34", "message":"User verified successfully" }
```

Response 404
```json
{ "status": "failure", "message": "User not found or inactive" }
```

Notes
- First request may be ~2s; subsequent within 5s are cached and faster.

---

## Teams

### Create Team
- **POST** `/api/teams/`
- Auth required

Request
```json
{ "team_name": "Warriors Alpha" }
```

Response 201
```json
{ "team_id":"TEAM-XXXXXX", "team_name":"Warriors Alpha", "user":"<user_id>", "user_name":"John Doe", "total_games":0, "created_at":"...", "updated_at":"...", "is_active":true }
```

### List My Teams
- **GET** `/api/teams/`
- Auth required

Response 200
```json
{ "teams": [{"team_id":"TEAM-...","team_name":"...","user":"...","user_name":"...","total_games":5,"created_at":"...","updated_at":"...","is_active":true}], "count": 2 }
```

### Get Team Detail
- **GET** `/api/teams/<team_id>/`
- Auth required

Response 200
```json
{
  "team_id":"TEAM-...",
  "team_name":"Warriors",
  "user":"<owner_user_id>",
  "created_at":"...",
  "updated_at":"...",
  "is_active":true,
  "game_results": [
    { "result_id":"RESULT-...","user":"...","user_name":"...","team":"TEAM-...","team_name":"...","game":"GAME-...","game_name":"...","points_scored":75,"played_at":"...","notes":"...","verified_by_admin":false,"admin_user":null,"admin_name":null }
  ],
  "total_points": 175
}
```

### Update Team
- **PUT** `/api/teams/<team_id>/`
- Auth required (owner only)

Request
```json
{ "team_name": "Warriors Beta" }
```

Response 200
```json
{ "team_id":"TEAM-...","team_name":"Warriors Beta","user":"...","user_name":"John Doe","total_games":5,"created_at":"...","updated_at":"...","is_active":true }
```

### Delete Team (Soft Delete)
- **DELETE** `/api/teams/<team_id>/`
- Auth required (owner only)

Response 200
```json
{ "message": "Team deleted successfully" }
```

---

## Games

### List Games
- **GET** `/api/games/`
- Auth required

Response 200
```json
{ "games": [{ "game_id":"GAME-...","game_name":"Basketball","game_description":"...","max_points":100,"min_points":0,"is_active":true,"total_plays":25,"created_at":"...","updated_at":"..." }], "count": 10 }
```

### Admin Create/Update Game
- **POST** `/api/admin/games/` (admin only)
- **PUT** `/api/admin/games/<game_id>/` (admin only)

Create Request
```json
{ "game_name": "Test Game", "game_description": "Created via admin", "max_points": 100, "min_points": 0 }
```

Create Response 201
```json
{ "game_id":"GAME-...","game_name":"Test Game","game_description":"Created via admin","max_points":100,"min_points":0,"is_active":true,"total_plays":0,"created_at":"...","updated_at":"..." }
```

Update Request
```json
{ "game_description": "Updated", "max_points": 120 }
```

Update Response 200
```json
{ "game_id":"GAME-...","game_name":"Test Game","game_description":"Updated","max_points":120,"min_points":0,"is_active":true,"total_plays":0,"created_at":"...","updated_at":"..." }
```

---

## Results

### Create Result
- **POST** `/api/results/`
- Auth required

Request
```json
{ "team": "TEAM-XXXXXX", "game": "GAME-YYYYYY", "points_scored": 85, "notes": "Great performance!" }
```

Response 201
```json
{ "result_id":"RESULT-...","user":"<user_id>","user_name":"John Doe","team":"TEAM-...","team_name":"Warriors","game":"GAME-...","game_name":"Basketball","points_scored":85,"played_at":"...","notes":"Great performance!","verified_by_admin":false,"admin_user":null,"admin_name":null }
```

Validation
- `points_scored` must be between the game’s `min_points` and `max_points`.

### List My Results
- **GET** `/api/results/`
- Auth required

Response 200
```json
{ "results": [{"result_id":"RESULT-...","game_name":"...","team_name":"...","points_scored":85,"played_at":"...","verified_by_admin":false}], "count": 12 }
```

---

## Admin Results

### List All Results (Admin)
- **GET** `/api/admin/results/`
- Admin only
- Supports filtering by `user_id`, `team_id`, `game_id`

Examples
```bash
# All
curl -H "Authorization: Bearer <admin_token>" http://localhost:8000/api/admin/results/

# Filter by user
curl -H "Authorization: Bearer <admin_token>" "http://localhost:8000/api/admin/results/?user_id=6905..."

# Filter by team
curl -H "Authorization: Bearer <admin_token>" "http://localhost:8000/api/admin/results/?team_id=TEAM-ABCD1234"

# Filter by game
curl -H "Authorization: Bearer <admin_token>" "http://localhost:8000/api/admin/results/?game_id=GAME-XYZ98765"
```

Response 200
```json
{ "results": [ {"result_id":"RESULT-...","user_name":"...","team_name":"...","game_name":"...","points_scored":95,"verified_by_admin":true,"admin_name":"Admin User"} ], "count": 120 }
```

### Update Result (Admin)
- **PUT** `/api/admin/results/<result_id>/`
- Admin only

Request
```json
{ "points_scored": 95, "verified_by_admin": true, "notes": "Verified by admin" }
```

Response 200
```json
{ "result_id":"RESULT-...","points_scored":95,"verified_by_admin":true,"admin_user":"<admin_id>","admin_name":"Admin User","notes":"Verified by admin" }
```

---

## Common Errors

- **400 Bad Request**
  - Validation errors (missing fields, invalid `points_scored`, etc.)
  - Example: `{ "team": ["Invalid pk \"TEAM-INVALID\" - object does not exist."] }`

- **401 Unauthorized**
  - Missing/invalid token
  - Example: `{ "detail": "Authentication credentials were not provided." }`

- **403 Forbidden**
  - Insufficient permissions (non-admin calling admin endpoints)
  - Example: `{ "error": "Admin access required" }`

- **404 Not Found**
  - Resource does not exist or not owned by user
  - Example: `{ "error": "Team not found" }`

- **500 Internal Server Error**
  - Unexpected error – see server logs in `logs/django.log`

---

## Status Codes

- **200 OK** – Successful read/update
- **201 Created** – Resource successfully created
- **400 Bad Request** – Validation error or malformed request
- **401 Unauthorized** – Missing/invalid credentials
- **403 Forbidden** – Not enough permissions
- **404 Not Found** – Resource not found
- **500 Internal Server Error** – Server error

---

## Notes & Best Practices
- **IDs:**
  - `User.id` is a 24-char string (MongoDB ObjectId as string)
  - `team_id`, `game_id`, `result_id` are formatted as `TEAM-xxxx`, `GAME-xxxx`, `RESULT-xxxx`
- **QR Codes:** Available via `qr_image_url` after registration/login
- **Performance:**
  - QR verification cached for 5 seconds
  - Indexed fields: `users_user.qr_id`, `users_user.email`
- **Soft Delete:** `DELETE /api/teams/<team_id>/` sets `is_active=false`

---

## Quick Smoke Test
```bash
# Register
curl -X POST http://localhost:8000/api/register/ -H "Content-Type: application/json" -d '{"name":"Test","email":"test@test.com","password":"Pass123!","password_confirm":"Pass123!"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/login/ -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"Pass123!"}' | python -c "import sys, json; print(json.load(sys.stdin)['tokens']['access'])")

# Create Team
curl -X POST http://localhost:8000/api/teams/ -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"team_name":"My Team"}'

# List Games
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/games/
```
