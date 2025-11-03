# Vercel Deployment Troubleshooting Guide

## Current Status: 500 Internal Server Error

Your deployment is live at `https://qr-backend-rho.vercel.app` but returning 500 errors on all endpoints.

---

## Root Cause

The 500 errors indicate that:
1. ✅ Routing is working (no more 404s)
2. ❌ Django application is failing to start
3. ❌ Likely missing environment variables or dependencies

---

## Fix Steps

### Step 1: Add Environment Variables in Vercel

Go to: https://vercel.com/dashboard → Your Project → Settings → Environment Variables

Add these **REQUIRED** variables:

```bash
# Django Core
SECRET_KEY=django-insecure-dev-key-change-in-production-12345678901234567890
DEBUG=False
DJANGO_SETTINGS_MODULE=qr_access_backend.settings

# Database
MONGODB_URI=mongodb+srv://syo358814_db_user:mK2hpHOWlxktrlX5@cluster0.8hto9nz.mongodb.net/qr_access_system?retryWrites=true&w=majority

# CORS
CORS_ALLOWED_ORIGINS=https://qr-backend-rho.vercel.app,http://localhost:3000

# Optional
ALLOWED_HOSTS=.vercel.app,.now.sh
```

**Important**: After adding variables, you MUST redeploy:
```bash
vercel --prod
```

### Step 2: Check Vercel Logs

View real-time logs to see the actual error:

```bash
vercel logs https://qr-backend-rho.vercel.app
```

Look for errors like:
- `ModuleNotFoundError` - Missing dependencies
- `ImproperlyConfigured` - Missing settings
- `Connection refused` - Database issues

### Step 3: Verify Dependencies

Ensure `requirements.txt` has all needed packages:

```txt
Django==4.1.13
djangorestframework==3.14.0
djongo==1.3.6
pymongo==3.12.3
dnspython==2.8.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.1
python-dotenv==1.0.0
qrcode==7.4.2
Pillow>=10.0.0
pytz==2023.3
```

### Step 4: Common Django + Vercel Issues

#### Issue: Static Files
Vercel serverless doesn't serve static files well.

**Solution**: Use WhiteNoise or CDN
```bash
pip install whitenoise
```

Add to `settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest
]
```

#### Issue: Database Connections
MongoDB Atlas connections may timeout in serverless.

**Solution**: Already using MongoDB Atlas (good!)
Ensure `dnspython` is installed for `mongodb+srv://` URIs.

#### Issue: File Uploads (QR Codes)
Vercel serverless has no persistent storage.

**Solution**: Use AWS S3, Cloudinary, or similar for QR codes.

---

## Alternative: Railway (Highly Recommended)

Django works MUCH better on Railway. Here's why:

| Feature | Vercel | Railway |
|---------|--------|---------|
| Django Support | ⚠️ Limited | ✅ Native |
| File Storage | ❌ No | ✅ Yes |
| Database Connections | ⚠️ Timeouts | ✅ Persistent |
| Cold Starts | ❌ Yes | ✅ No |
| Configuration | 🔧 Complex | ✅ Simple |
| Cost | 💰 $20/mo | 💰 Free tier |

### Deploy to Railway in 2 Minutes:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Add environment variables in Railway dashboard
# Done! Your app is live at: https://your-app.railway.app
```

Railway will:
- ✅ Auto-detect Django
- ✅ Install dependencies
- ✅ Run migrations
- ✅ Serve static files
- ✅ Provide persistent storage
- ✅ Connect to MongoDB Atlas

---

## Quick Test Commands

After fixing, test with:

```bash
# Health check
curl https://qr-backend-rho.vercel.app/api/health/

# Register user
curl -X POST https://qr-backend-rho.vercel.app/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
  }'

# Or run the test script
python test_vercel_deployment.py
```

---

## Expected Results After Fix

```
✅ Health Check - Status: 200
✅ User Registration - Status: 201
✅ User Login - Status: 200
✅ Get Current User - Status: 200
✅ Create Team - Status: 201
✅ List Games - Status: 200
```

---

## Need Help?

1. **Check Vercel logs**: `vercel logs`
2. **Check environment variables**: Vercel Dashboard → Settings → Environment Variables
3. **Try Railway**: Much easier for Django
4. **Contact support**: Vercel support or Django community

---

## Summary

**Current Issue**: 500 errors due to missing environment variables

**Quick Fix**:
1. Add environment variables in Vercel Dashboard
2. Redeploy: `vercel --prod`
3. Test: `python test_vercel_deployment.py`

**Best Solution**: Deploy to Railway instead for native Django support.

---

**Last Updated**: November 4, 2025, 12:10 AM UTC+3
