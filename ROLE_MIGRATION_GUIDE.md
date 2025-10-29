# Role Field Migration Guide

## Overview

The User model now includes a `role` field that can be either **"user"** or **"admin"**. This guide explains how to add the role field to your existing database.

## What's New

### User Model Changes

```python
class User(AbstractBaseUser, PermissionsMixin):
    # New field added
    role = models.CharField(
        max_length=10,
        choices=[('user', 'User'), ('admin', 'Admin')],
        default='user',
        db_index=True,
        help_text="User role: 'user' or 'admin'"
    )
```

### New Features

1. **Role-based Registration**: Users can optionally specify role during registration
2. **Role in Responses**: All API responses now include the user's role
3. **Role-based Permissions**: New permission classes for admin-only endpoints
4. **Admin Method**: New `is_admin()` method to check if user has admin privileges

---

## Migration Steps

### Step 1: Run Django Migrations

```bash
# Create migration file
python manage.py makemigrations users

# Apply migration to database
python manage.py migrate users
```

### Step 2: Update Existing Users in MongoDB

If you already have users in your MongoDB database, they will automatically get the default role of **"user"** when accessed through Django.

However, if you want to manually update existing users in MongoDB, use this script:

#### Option A: Update All Existing Users to "user" Role

```python
# Run this in Django shell
python manage.py shell

from users.models import User

# Update all users without a role to 'user'
User.objects.filter(role__isnull=True).update(role='user')
# Or for empty string
User.objects.filter(role='').update(role='user')

print("All users updated!")
```

#### Option B: Update Specific Users to "admin" Role

```python
# Run this in Django shell
python manage.py shell

from users.models import User

# Update specific users to admin
admin_emails = ['mohammad@example.com', 'admin@example.com']
User.objects.filter(email__in=admin_emails).update(role='admin')

print("Admin users updated!")
```

#### Option C: Direct MongoDB Update (if needed)

```javascript
// Connect to MongoDB shell
mongo

// Use your database
use qr_access_system

// Update all users without role to 'user'
db.users_user.updateMany(
  { role: { $exists: false } },
  { $set: { role: "user" } }
)

// Update specific user to admin
db.users_user.updateOne(
  { email: "mohammad@example.com" },
  { $set: { role: "admin" } }
)

// Verify
db.users_user.find({}, { email: 1, role: 1 })
```

---

## API Changes

### 1. Registration Endpoint

**Previous Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123"
}
```

**New Request (with optional role):**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "role": "admin"  // Optional: "user" or "admin", defaults to "user"
}
```

**Response Now Includes Role:**
```json
{
  "user": {
    "id": "...",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",  // NEW
    "qr_id": "QR-A1B2C3D4",
    "qr_image_url": "..."
  },
  "tokens": { ... }
}
```

### 2. Login Endpoint

**Response Now Includes Role:**
```json
{
  "user": {
    "id": "...",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",  // NEW
    "qr_id": "QR-A1B2C3D4",
    "qr_image_url": "..."
  },
  "tokens": { ... }
}
```

### 3. QR Verification Endpoint

**Response Now Includes Role:**
```json
{
  "status": "success",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",  // NEW
  "qr_id": "QR-A1B2C3D4",
  "message": "User verified successfully"
}
```

### 4. User List & Detail Endpoints

All user endpoints now include the `role` field in responses.

---

## Using Role-Based Permissions

### Import Custom Permissions

```python
from users.permissions import IsAdminUser, IsAdminOrReadOnly, IsOwnerOrAdmin
```

### Example: Admin-Only View

```python
from rest_framework.views import APIView
from users.permissions import IsAdminUser

class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        return Response({"message": "Admin access granted"})
```

### Example: Check Role in View

```python
def my_view(request):
    if request.user.is_admin():
        # Admin-specific logic
        return Response({"message": "Admin access"})
    else:
        # Regular user logic
        return Response({"message": "User access"})
```

---

## Testing

### Test Role Field

```bash
# Test registration with role
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin User",
    "email": "admin@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "role": "admin"
  }'

# Test QR verification (should include role)
curl http://localhost:8000/api/verify/<QR_ID>/
```

### Check User Roles in Django Shell

```python
python manage.py shell

from users.models import User

# Get all users and their roles
for user in User.objects.all():
    print(f"{user.email}: {user.role}")

# Check if user is admin
user = User.objects.get(email='mohammad@example.com')
print(f"Is admin: {user.is_admin()}")
```

---

## Frontend Integration

### Flutter Example

```dart
class UserModel {
  final String id;
  final String name;
  final String email;
  final String role;  // NEW
  final String qrId;
  
  UserModel.fromJson(Map<String, dynamic> json)
      : id = json['id'],
        name = json['name'],
        email = json['email'],
        role = json['role'],  // NEW
        qrId = json['qr_id'];
  
  bool get isAdmin => role == 'admin';  // NEW
}
```

### React Example

```javascript
interface User {
  id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';  // NEW
  qr_id: string;
}

const user: User = await response.json();
const isAdmin = user.role === 'admin';  // NEW
```

---

## Backward Compatibility

- **Default Role**: All new users get `role="user"` by default
- **Existing Users**: Will have `role="user"` after migration
- **Optional Field**: Role is optional during registration
- **Superusers**: Automatically get `role="admin"`

---

## Admin Interface

The Django admin interface now includes:

1. **Role in List View**: See user roles at a glance
2. **Role Filter**: Filter users by role
3. **Role in Form**: Edit user roles easily

Access at: `http://localhost:8000/admin/users/user/`

---

## Troubleshooting

### Issue: Migration Error

**Problem**: Migration fails with field error

**Solution**:
```bash
# Delete migration files (keep __init__.py)
rm users/migrations/0002_*.py

# Recreate migrations
python manage.py makemigrations users
python manage.py migrate users
```

### Issue: Existing Users Missing Role

**Problem**: API returns users without role field

**Solution**:
```python
# Django shell
from users.models import User
User.objects.filter(role__isnull=True).update(role='user')
```

### Issue: MongoDB Direct Edit Not Reflecting

**Problem**: Changed role in MongoDB but Django doesn't show it

**Solution**: Restart Django server
```bash
python manage.py runserver
```

---

## Summary of Changes

| Component | Change |
|-----------|--------|
| **User Model** | Added `role` field with choices |
| **Serializers** | Include role in all user serializers |
| **Views** | Return role in registration, login, and verification |
| **Admin** | Display and filter by role |
| **Permissions** | New role-based permission classes |

---

## Next Steps

1. ✅ Run migrations
2. ✅ Update existing users with roles
3. ✅ Test API endpoints
4. ✅ Update frontend to handle role field
5. ✅ Implement role-based UI features

---

For questions or issues, refer to the main README.md or API documentation.
