# Role Field - Usage Examples

## Quick Reference

### Role Values
- **"user"** - Regular user (default)
- **"admin"** - Administrator with elevated privileges

---

## API Examples

### 1. Register Regular User (Default)

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

**Response:**
```json
{
  "user": {
    "id": "...",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "qr_id": "QR-A1B2C3D4",
    "qr_image_url": "..."
  },
  "tokens": { ... }
}
```

### 2. Register Admin User

```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin User",
    "email": "admin@example.com",
    "password": "adminpass123",
    "password_confirm": "adminpass123",
    "role": "admin"
  }'
```

**Response:**
```json
{
  "user": {
    "id": "...",
    "name": "Admin User",
    "email": "admin@example.com",
    "role": "admin",
    "qr_id": "QR-B2C3D4E5",
    "qr_image_url": "..."
  },
  "tokens": { ... }
}
```

### 3. Login (Returns Role)

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "adminpass123"
  }'
```

**Response includes role:**
```json
{
  "user": {
    "role": "admin",
    ...
  },
  "tokens": { ... }
}
```

### 4. QR Verification (Includes Role)

```bash
curl http://localhost:8000/api/verify/QR-A1B2C3D4/
```

**Response:**
```json
{
  "status": "success",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "qr_id": "QR-A1B2C3D4",
  "message": "User verified successfully"
}
```

---

## Python Examples

### Check User Role in Django

```python
from users.models import User

# Get user
user = User.objects.get(email='john@example.com')

# Check role
if user.role == 'admin':
    print("User is an admin")
else:
    print("User is a regular user")

# Using the is_admin() method
if user.is_admin():
    print("User has admin privileges")
```

### Create Users with Roles

```python
from users.models import User

# Create regular user
user = User.objects.create_user(
    email='user@example.com',
    name='Regular User',
    password='password123',
    role='user'  # Optional, defaults to 'user'
)

# Create admin user
admin = User.objects.create_user(
    email='admin@example.com',
    name='Admin User',
    password='password123',
    role='admin'
)

# Create superuser (automatically gets admin role)
superuser = User.objects.create_superuser(
    email='super@example.com',
    name='Super Admin',
    password='password123'
)
print(superuser.role)  # 'admin'
```

### Update User Role

```python
from users.models import User

# Promote user to admin
user = User.objects.get(email='user@example.com')
user.role = 'admin'
user.save()

# Demote admin to user
admin = User.objects.get(email='admin@example.com')
admin.role = 'user'
admin.save()

# Bulk update
User.objects.filter(email__in=['user1@example.com', 'user2@example.com']).update(role='admin')
```

### Filter Users by Role

```python
from users.models import User

# Get all admins
admins = User.objects.filter(role='admin')
for admin in admins:
    print(f"Admin: {admin.email}")

# Get all regular users
users = User.objects.filter(role='user')
for user in users:
    print(f"User: {user.email}")

# Count by role
admin_count = User.objects.filter(role='admin').count()
user_count = User.objects.filter(role='user').count()
print(f"Admins: {admin_count}, Users: {user_count}")
```

---

## Using Custom Permissions

### Admin-Only View

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from users.permissions import IsAdminUser

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        return Response({
            "message": "Welcome to admin dashboard",
            "user": request.user.email,
            "role": request.user.role
        })
```

**Test:**
```bash
# This will fail for regular users
curl http://localhost:8000/api/admin/dashboard/ \
  -H "Authorization: Bearer <regular_user_token>"

# This will succeed for admins
curl http://localhost:8000/api/admin/dashboard/ \
  -H "Authorization: Bearer <admin_user_token>"
```

### Read-Only for Users, Full Access for Admins

```python
from rest_framework.views import APIView
from users.permissions import IsAdminOrReadOnly

class SettingsView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    
    def get(self, request):
        # Anyone authenticated can read
        return Response({"settings": "..."})
    
    def post(self, request):
        # Only admins can modify
        return Response({"message": "Settings updated"})
```

### Owner or Admin Access

```python
from rest_framework import generics
from users.permissions import IsOwnerOrAdmin
from users.models import User
from users.serializers import UserDetailSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsOwnerOrAdmin]
    
    def get_object(self):
        # Users can access their own profile
        # Admins can access any profile
        return User.objects.get(id=self.kwargs['id'])
```

---

## Frontend Examples

### JavaScript/TypeScript

```typescript
// Type definition
interface User {
  id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';
  qr_id: string;
  qr_image_url: string;
}

// Check if user is admin
function isAdmin(user: User): boolean {
  return user.role === 'admin';
}

// Conditional rendering
function renderDashboard(user: User) {
  if (isAdmin(user)) {
    return <AdminDashboard user={user} />;
  } else {
    return <UserDashboard user={user} />;
  }
}

// Register with role
async function registerUser(data: {
  name: string;
  email: string;
  password: string;
  role?: 'user' | 'admin';
}) {
  const response = await fetch('http://localhost:8000/api/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...data,
      password_confirm: data.password,
      role: data.role || 'user'
    })
  });
  return response.json();
}
```

### React Component

```jsx
function UserRoleBadge({ role }) {
  return (
    <span className={`badge ${role === 'admin' ? 'badge-admin' : 'badge-user'}`}>
      {role === 'admin' ? '👑 Admin' : '👤 User'}
    </span>
  );
}

function UserList({ users }) {
  return (
    <div>
      {users.map(user => (
        <div key={user.id} className="user-card">
          <h3>{user.name}</h3>
          <p>{user.email}</p>
          <UserRoleBadge role={user.role} />
        </div>
      ))}
    </div>
  );
}
```

### Flutter/Dart

```dart
class User {
  final String id;
  final String name;
  final String email;
  final String role;
  final String qrId;
  
  User({
    required this.id,
    required this.name,
    required this.email,
    required this.role,
    required this.qrId,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
      role: json['role'],
      qrId: json['qr_id'],
    );
  }
  
  bool get isAdmin => role == 'admin';
  bool get isUser => role == 'user';
}

// Usage in widget
Widget buildUserCard(User user) {
  return Card(
    child: ListTile(
      title: Text(user.name),
      subtitle: Text(user.email),
      trailing: user.isAdmin 
        ? Icon(Icons.admin_panel_settings, color: Colors.red)
        : Icon(Icons.person, color: Colors.blue),
    ),
  );
}

// Conditional navigation
void navigateToDashboard(User user) {
  if (user.isAdmin) {
    Navigator.pushNamed(context, '/admin-dashboard');
  } else {
    Navigator.pushNamed(context, '/user-dashboard');
  }
}
```

---

## Raspberry Pi Integration

### Python Script with Role Check

```python
import requests

API_URL = 'http://localhost:8000/api'

def verify_qr_with_role(qr_id):
    """Verify QR code and check user role."""
    response = requests.get(f'{API_URL}/verify/{qr_id}/')
    
    if response.status_code == 200:
        data = response.json()
        
        if data['status'] == 'success':
            name = data['name']
            role = data['role']
            
            print(f"✅ Access granted: {name}")
            
            if role == 'admin':
                print("👑 Admin access - Full privileges")
                # Grant admin-level access
                return 'admin'
            else:
                print("👤 User access - Standard privileges")
                # Grant user-level access
                return 'user'
        else:
            print("❌ Access denied")
            return None
    else:
        print("❌ Verification failed")
        return None

# Usage
qr_id = input("Scan QR Code: ")
access_level = verify_qr_with_role(qr_id)

if access_level == 'admin':
    # Open admin door, enable all features
    pass
elif access_level == 'user':
    # Open regular door, enable basic features
    pass
else:
    # Deny access
    pass
```

---

## MongoDB Queries

### Direct MongoDB Queries

```javascript
// Connect to MongoDB
mongo

use qr_access_system

// Find all admins
db.users_user.find({ role: "admin" }, { name: 1, email: 1, role: 1 })

// Find all users
db.users_user.find({ role: "user" }, { name: 1, email: 1, role: 1 })

// Count by role
db.users_user.countDocuments({ role: "admin" })
db.users_user.countDocuments({ role: "user" })

// Update user to admin
db.users_user.updateOne(
  { email: "user@example.com" },
  { $set: { role: "admin" } }
)

// Update multiple users to admin
db.users_user.updateMany(
  { email: { $in: ["user1@example.com", "user2@example.com"] } },
  { $set: { role: "admin" } }
)

// Find users without role (after migration)
db.users_user.find({ role: { $exists: false } })

// Set default role for users without one
db.users_user.updateMany(
  { role: { $exists: false } },
  { $set: { role: "user" } }
)
```

---

## Summary

### Key Points

1. **Default Role**: New users get `role="user"` automatically
2. **Optional Registration**: Role can be specified during registration
3. **Role in Responses**: All API endpoints return the role field
4. **Helper Method**: Use `user.is_admin()` to check admin status
5. **Custom Permissions**: Use `IsAdminUser`, `IsAdminOrReadOnly`, `IsOwnerOrAdmin`
6. **Superusers**: Automatically get `role="admin"`

### Best Practices

- ✅ Always check role on sensitive operations
- ✅ Use custom permission classes for views
- ✅ Display role badges in UI
- ✅ Log role-based actions for security
- ✅ Implement different UI flows for different roles

---

For more information, see:
- `ROLE_MIGRATION_GUIDE.md` - Migration steps
- `API_DOCUMENTATION.md` - Complete API reference
- `README.md` - Project overview
