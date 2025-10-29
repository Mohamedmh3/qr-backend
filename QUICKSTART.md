# 🚀 Quick Start - Get Running in 5 Minutes

## Step 1: Install Dependencies (2 min)

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Start MongoDB (1 min)

```bash
# Start MongoDB service
net start MongoDB
```

**OR using Docker:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Step 3: Initialize Database (1 min)

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser
```

## Step 4: Start Server (1 min)

```bash
# Option 1: Use the batch script
start_server.bat

# Option 2: Manual start
python manage.py runserver
```

✅ **Server running at:** http://localhost:8000

---

## 🧪 Quick Test

```bash
# Test registration
curl -X POST http://localhost:8000/api/register/ -H "Content-Type: application/json" -d "{\"name\":\"Test User\",\"email\":\"test@example.com\",\"password\":\"testpass123\",\"password_confirm\":\"testpass123\"}"

# Run automated tests
python test_api.py
```

---

## 📋 Essential URLs

- **API Base:** http://localhost:8000/api
- **Admin Panel:** http://localhost:8000/admin
- **QR Codes:** http://localhost:8000/media/qr_codes/

## 🔑 Default Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/register/` | POST | No | Register user |
| `/api/login/` | POST | No | Login user |
| `/api/verify/<qr_id>/` | GET | No | Verify QR |
| `/api/users/` | GET | Yes | List users |

## 📚 Need More Help?

- **Detailed Setup:** See `SETUP_GUIDE.md`
- **API Docs:** See `API_DOCUMENTATION.md`
- **Full README:** See `README.md`

---

**Ready to integrate?** Connect your Flutter app to `http://localhost:8000/api` 🎉
