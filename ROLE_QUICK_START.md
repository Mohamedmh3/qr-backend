# Role Feature - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Run Migrations (1 min)

```bash
python manage.py makemigrations users
python manage.py migrate users
```

### Step 2: Update Existing Users (1 min)

```bash
# Option A: Interactive script
python manage.py shell < add_roles_to_users.py

# Option B: Django shell
python manage.py shell
>>> from users.models import User
>>> User.objects.all().update(role='user')
>>> User.objects.filter(email='mohammad@example.com').update(role='admin')
>>> exit()
```

### Step 3: Restart Server & Test

```bash
python manage.py runserver
```

**Test it:**
```bash
curl http://localhost:8000/api/verify/QR-A1B2C3D4/
# Should now return role field!
```

---

## 📋 What's New

### API Responses Now Include Role:

**Registration:**
```json
{
  "user": {
    "name": "John",
    "email": "john@example.com",
    "role": "user",  ← NEW!
    "qr_id": "QR-A1B2C3D4"
  }
}
```

**QR Verification:**
```json
{
  "status": "success",
  "name": "John",
  "role": "user",  ← NEW!
  "qr_id": "QR-A1B2C3D4"
}
```

---

## 🎯 Common Tasks

### Create Admin User
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin",
    "email": "admin@example.com",
    "password": "pass123",
    "password_confirm": "pass123",
    "role": "admin"
  }'
```

### Promote User to Admin (Django Shell)
```python
from users.models import User
user = User.objects.get(email='user@example.com')
user.role = 'admin'
user.save()
```

### Check User Role (Python)
```python
if user.is_admin():
    print("Admin access")
else:
    print("User access")
```

---

## 📚 Full Documentation

- **Migration Guide:** `ROLE_MIGRATION_GUIDE.md`
- **Usage Examples:** `ROLE_USAGE_EXAMPLES.md`
- **Complete Summary:** `ROLE_FEATURE_SUMMARY.md`

---

## ✅ That's it!

Your backend now supports roles. Update your frontend to use the `role` field!
