# Deployment Checklist for Render

## Pre-Deployment Steps

### 1. GitHub Repository Setup
- [ ] Ensure all changes are committed and pushed to GitHub
- [ ] Verify `.gitignore` is properly configured
- [ ] Check that no sensitive files (`.env`, database files) are in the repository

### 2. Render Account Setup
- [ ] Create Render account at [render.com](https://render.com)
- [ ] Verify account is activated

### 3. Database Setup
- [ ] Create a new PostgreSQL database service on Render
- [ ] Note the database connection details

## Deployment Steps

### Option 1: Automatic Deployment (Recommended)
1. **Connect Repository**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `finance-tracker` repository

2. **Automatic Configuration**
   - Render will detect the `render.yaml` file
   - Service will be automatically configured
   - Database will be created automatically

3. **Verify Deployment**
   - Check build logs for any errors
   - Verify the service is running
   - Test the health endpoint: `https://your-app.onrender.com/health/`

### Option 2: Manual Deployment
1. **Create Web Service**
   - Name: `finance-tracker`
   - Environment: `Python`
   - Region: Choose closest to your users
   - Branch: `main` (or your default branch)

2. **Build & Deploy Settings**
   - Build Command: `./build.sh`
   - Start Command: `gunicorn finance_tracker.wsgi:application`

3. **Environment Variables**
   - `PYTHON_VERSION`: `3.11.0`
   - `SECRET_KEY`: Generate a secure key (or let Render generate it)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com`

4. **Database Connection**
   - Create a PostgreSQL database service
   - Copy the `DATABASE_URL` to your web service environment variables

## Post-Deployment Verification

### 1. Basic Functionality
- [ ] Homepage loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] Database operations work

### 2. Security Check
- [ ] HTTPS is enforced
- [ ] Debug mode is disabled
- [ ] Secret key is properly set
- [ ] Allowed hosts are configured

### 3. Performance Check
- [ ] Static files are served correctly
- [ ] Database queries are optimized
- [ ] Page load times are acceptable

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check build logs for dependency issues
   - Verify `requirements.txt` is up to date
   - Ensure `build.sh` is executable

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is set correctly
   - Check database service is running
   - Ensure database credentials are correct

3. **Static Files Not Loading**
   - Check `STATIC_ROOT` configuration
   - Verify `collectstatic` ran successfully
   - Check whitenoise middleware configuration

4. **500 Errors**
   - Check application logs in Render dashboard
   - Verify environment variables are set
   - Check database migrations ran successfully

### Useful Commands

```bash
# Check Django configuration
python manage.py check --deploy

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-secret-key-here` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `.onrender.com` |
| `DATABASE_URL` | Database connection | `postgres://user:pass@host:port/db` |
| `PYTHON_VERSION` | Python version | `3.11.0` |

## Support

If you encounter issues:
1. Check Render's documentation: [docs.render.com](https://docs.render.com)
2. Review Django deployment checklist: [docs.djangoproject.com](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
3. Check Render service logs for detailed error messages
