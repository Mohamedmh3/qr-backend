# QR Access Verification System - Backend

A production-grade Django REST API backend for QR-based access verification. Built with Django, Django REST Framework, MongoDB, and JWT authentication.

## 🎯 Features

- **User Authentication**: Register, login, and logout with JWT tokens
- **Automatic QR Code Generation**: Each user gets a unique QR ID and QR code image
- **QR Verification**: Raspberry Pi can verify users via QR code
- **Admin Management**: Add and delete users through API
- **Secure & Scalable**: Production-ready with proper error handling and logging

## 🧱 Tech Stack

- **Backend Framework**: Django 4.2 + Django REST Framework
- **Database**: MongoDB (via djongo)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **QR Code Generation**: Python qrcode + Pillow
- **CORS**: Enabled for Flutter and React apps

## 📁 Project Structure

```
qr-backend/
│
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables
├── .gitignore                    # Git ignore file
│
├── qr_access_backend/            # Main project directory
│   ├── __init__.py
│   ├── settings.py               # Django settings (MongoDB, JWT, CORS)
│   ├── urls.py                   # Main URL router
│   └── wsgi.py                   # WSGI configuration
│
├── users/                        # User management app
│   ├── __init__.py
│   ├── models.py                 # User model with QR fields
│   ├── serializers.py            # DRF serializers
│   ├── views.py                  # API views
│   ├── urls.py                   # App URL routes
│   └── admin.py                  # Django admin config
│
├── utils/                        # Utility modules
│   ├── __init__.py
│   └── qr_generator.py           # QR code generation logic
│
├── media/                        # Media files (created automatically)
│   └── qr_codes/                 # QR code images
│
└── logs/                         # Application logs (created automatically)
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- MongoDB (local or remote)
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
cd qr-backend
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=qr_access_system
DB_HOST=localhost
DB_PORT=27017

# CORS Origins (comma-separated)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### Step 5: Start MongoDB

Ensure MongoDB is running on your system:

```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### Step 6: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 8: Start Development Server

```bash
python manage.py runserver
```

The API will be available at: **http://localhost:8000**

## 🔐 API Endpoints

### Authentication Endpoints

#### 1. **Register User**
```http
POST /api/register/
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}

Response (201):
{
  "user": {
    "id": "...",
    "name": "John Doe",
    "email": "john@example.com",
    "qr_id": "QR-A1B2C3D4",
    "qr_image_url": "http://localhost:8000/media/qr_codes/QR-A1B2C3D4.png"
  },
  "tokens": {
    "refresh": "...",
    "access": "..."
  },
  "message": "User registered successfully"
}
```

#### 2. **Login**
```http
POST /api/login/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}

Response (200):
{
  "user": { ... },
  "tokens": { ... },
  "message": "Login successful"
}
```

#### 3. **Logout**
```http
POST /api/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}

Response (205):
{
  "message": "Logout successful"
}
```

### QR Verification Endpoint (Raspberry Pi)

#### 4. **Verify QR Code**
```http
GET /api/verify/<qr_id>/

Response (200) - User Found:
{
  "status": "success",
  "name": "John Doe",
  "email": "john@example.com",
  "qr_id": "QR-A1B2C3D4",
  "message": "User verified successfully"
}

Response (404) - User Not Found:
{
  "status": "failure",
  "message": "User not found or inactive"
}
```

### Admin Endpoints

#### 5. **List All Users**
```http
GET /api/users/
Authorization: Bearer <access_token>

Response (200):
{
  "count": 10,
  "users": [ ... ]
}
```

#### 6. **Get User Details**
```http
GET /api/users/<user_id>/
Authorization: Bearer <access_token>

Response (200):
{
  "id": "...",
  "name": "John Doe",
  "email": "john@example.com",
  "qr_id": "QR-A1B2C3D4",
  "qr_image_url": "...",
  ...
}
```

#### 7. **Delete User**
```http
DELETE /api/users/<user_id>/delete/
Authorization: Bearer <access_token>

Response (200):
{
  "message": "User john@example.com deleted successfully"
}
```

#### 8. **Get Current User**
```http
GET /api/me/
Authorization: Bearer <access_token>

Response (200):
{
  "id": "...",
  "name": "John Doe",
  ...
}
```

## 🔧 Configuration Details

### JWT Token Configuration

- **Access Token Lifetime**: 60 minutes (configurable)
- **Refresh Token Lifetime**: 1440 minutes / 24 hours (configurable)
- **Token Rotation**: Enabled
- **Token Blacklisting**: Enabled (for logout)

### CORS Configuration

The backend is configured to accept requests from:
- Flutter app: `http://localhost:3000`
- React dashboard: `http://localhost:5173`

You can add more origins in the `.env` file.

### Password Requirements

- Minimum length: 8 characters
- Must not be too similar to user information
- Must not be a commonly used password
- Must not be entirely numeric

## 📝 Usage Examples

### Using with Flutter App

```dart
// Register
final response = await http.post(
  Uri.parse('http://localhost:8000/api/register/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'name': 'John Doe',
    'email': 'john@example.com',
    'password': 'securepassword123',
    'password_confirm': 'securepassword123',
  }),
);
```

### Using with Raspberry Pi

```python
import requests

# Verify QR code
qr_id = "QR-A1B2C3D4"
response = requests.get(f'http://localhost:8000/api/verify/{qr_id}/')

if response.json()['status'] == 'success':
    print(f"Access granted for: {response.json()['name']}")
else:
    print("Access denied")
```

### Using with React Dashboard

```javascript
// Get all users
const response = await fetch('http://localhost:8000/api/users/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
});
const data = await response.json();
```

## 🔍 Testing

### Test Registration
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"testpass123","password_confirm":"testpass123"}'
```

### Test QR Verification
```bash
curl http://localhost:8000/api/verify/QR-A1B2C3D4/
```

## 📊 Database Schema

### User Model

| Field | Type | Description |
|-------|------|-------------|
| id | ObjectId | Primary key (MongoDB) |
| email | EmailField | Unique email address |
| name | CharField | User's full name |
| password | CharField | Hashed password |
| qr_id | CharField | Unique QR identifier |
| qr_image | CharField | Path to QR code image |
| is_active | BooleanField | Account active status |
| is_staff | BooleanField | Staff status |
| is_superuser | BooleanField | Superuser status |
| date_joined | DateTimeField | Registration timestamp |
| last_login | DateTimeField | Last login timestamp |

## 🛡️ Security Features

- ✅ Password hashing with Django's built-in utilities
- ✅ JWT token authentication
- ✅ Token blacklisting for logout
- ✅ CORS protection
- ✅ Password validation
- ✅ Input sanitization
- ✅ SQL injection protection (via ORM)

## 📁 Media Files

QR code images are automatically stored in:
```
media/qr_codes/<QR_ID>.png
```

Example: `media/qr_codes/QR-A1B2C3D4.png`

## 🐛 Troubleshooting

### MongoDB Connection Error

```bash
# Check if MongoDB is running
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl status mongod
```

### Port 8000 Already in Use

```bash
# Run on different port
python manage.py runserver 8080
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [djongo Documentation](https://github.com/doableware/djongo)
- [Simple JWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)

## 👨‍💻 Development

### Code Style

This project follows:
- PEP 8 style guide
- Django coding style
- RESTful API best practices

### Logging

Logs are stored in `logs/django.log` with different levels:
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- DEBUG: Debug information (only in DEBUG mode)

## 🚀 Production Deployment

Before deploying to production:

1. Set `DEBUG=False` in `.env`
2. Change `SECRET_KEY` to a secure random value
3. Update `ALLOWED_HOSTS` with your domain
4. Configure a production-grade MongoDB instance
5. Use a proper web server (Gunicorn + Nginx)
6. Set up SSL/TLS certificates
7. Configure proper backup systems

## 📄 License

This project is developed for educational and commercial purposes.

## 🤝 Support

For issues or questions, please check the documentation or create an issue.

---

**Built with ❤️ using Django & Django REST Framework**
