# Django Backend Deployment to Vercel

## ✅ Recent Fixes (November 2025)

The following issues have been fixed to make the deployment work:

1. **WSGI Handler**: Changed from ASGI to WSGI in `vercel_handler.py`
   - Vercel's `@vercel/python` expects WSGI applications
   - Previous ASGI handler was causing `FUNCTION_INVOCATION_FAILED` errors

2. **Read-Only Filesystem**: Updated `settings.py` to handle Vercel's serverless environment
   - Disabled file logging on Vercel (console logging only)
   - Prevented directory creation (`logs/`, `media/qr_codes/`) on read-only filesystem
   - Added `IS_VERCEL` environment detection

3. **ALLOWED_HOSTS**: Fixed Vercel environment detection
   - Changed from `os.getenv('VERCEL', False)` to `os.getenv('VERCEL')`
   - Properly adds `.vercel.app` and `.now.sh` domains

### What Changed:
- ✅ `vercel_handler.py` - Now uses WSGI instead of ASGI
- ✅ `qr_access_backend/settings.py` - Serverless-friendly logging and directory handling
- ✅ `users/views.py` - Games endpoint no longer requires authentication

## ⚠️ Important Notice

**Vercel is NOT recommended for Django applications** because:
- Django is designed for long-running servers, not serverless functions
- File uploads (QR codes) won't persist on Vercel's serverless platform
- Database connections may timeout in serverless environment
- Cold starts can be slow for Django apps

### Better Alternatives:
1. **Railway** - Best for Django (https://railway.app)
2. **Render** - Great Django support (https://render.com)
3. **AWS Elastic Beanstalk** - Enterprise solution
4. **DigitalOcean App Platform** - Simple and reliable
5. **Heroku** - Classic Django hosting

---

## If You Still Want to Deploy to Vercel

### Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com
2. **Vercel CLI**: Install globally
   ```bash
   npm install -g vercel
   ```

### Step 1: Prepare Your Project

The following files have been created for you:
- ✅ `vercel.json` - Vercel configuration
- ✅ `build_files.sh` - Build script
- ✅ `.vercelignore` - Files to exclude from deployment

### Step 2: Environment Variables

You need to set these environment variables in Vercel:

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=.vercel.app,.now.sh

# Database - MongoDB Atlas (REQUIRED)
DB_NAME=qr_access_system
MONGODB_URI=mongodb+srv://syo358814_db_user:mK2hpHOWlxktrlX5@cluster0.8hto9nz.mongodb.net/qr_access_system?retryWrites=true&w=majority

# CORS Settings
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### Step 3: Deploy to Vercel

#### Option A: Deploy via Vercel CLI

1. Login to Vercel:
   ```bash
   vercel login
   ```

2. Navigate to your backend directory:
   ```bash
   cd d:\Development\QR-Project\qr-backend
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Follow the prompts:
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N** (first time)
   - Project name? `qr-access-backend` (or your choice)
   - Directory? `./` (current directory)
   - Override settings? **N**

5. For production deployment:
   ```bash
   vercel --prod
   ```

#### Option B: Deploy via GitHub

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Prepare for Vercel deployment"
   git remote add origin https://github.com/yourusername/qr-backend.git
   git push -u origin main
   ```

2. Go to https://vercel.com/new
3. Import your GitHub repository
4. Configure:
   - Framework Preset: **Other**
   - Root Directory: `./`
   - Build Command: `bash build_files.sh`
   - Output Directory: `staticfiles_build`
5. Add environment variables (see Step 2)
6. Click **Deploy**

### Step 4: Post-Deployment

1. **Test the API**:
   ```bash
   curl https://your-project.vercel.app/api/health/
   ```

2. **Update Frontend CORS**:
   - Add your Vercel backend URL to frontend API configuration
   - Update CORS_ALLOWED_ORIGINS in Vercel environment variables

3. **Monitor Logs**:
   ```bash
   vercel logs
   ```

### Known Limitations on Vercel

1. **File Storage**: QR code images won't persist
   - Solution: Use AWS S3, Cloudinary, or similar service
   
2. **Database Connections**: May timeout
   - Solution: Use connection pooling or MongoDB Atlas

3. **Cold Starts**: First request may be slow
   - Solution: Use Vercel's "Serverless Function Warming"

4. **Request Timeout**: 10 seconds for Hobby plan
   - Solution: Upgrade to Pro plan (60 seconds)

5. **No WebSocket Support**
   - Solution: Use separate WebSocket service

### Troubleshooting

#### Build Fails
- Check `vercel logs` for errors
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

#### 500 Internal Server Error
- Check environment variables are set correctly
- Verify MongoDB Atlas connection string
- Check `DEBUG=False` is set

#### Static Files Not Loading
- Run `vercel --prod` to rebuild
- Check `STATIC_ROOT` and `STATIC_URL` in settings

#### CORS Errors
- Add frontend domain to `CORS_ALLOWED_ORIGINS`
- Verify `corsheaders` is in `INSTALLED_APPS`

### Alternative: Deploy to Railway (Recommended)

Railway is much better suited for Django:

1. Sign up at https://railway.app
2. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```
3. Login and deploy:
   ```bash
   railway login
   railway init
   railway up
   ```
4. Add environment variables in Railway dashboard
5. Your app will have persistent storage and better performance

### Support

For issues specific to:
- **Vercel**: https://vercel.com/support
- **Django**: https://docs.djangoproject.com
- **This Project**: Check the main README.md

---

## Quick Commands Reference

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# List deployments
vercel ls

# Remove deployment
vercel rm <deployment-url>
```

---

**Last Updated**: November 2025
