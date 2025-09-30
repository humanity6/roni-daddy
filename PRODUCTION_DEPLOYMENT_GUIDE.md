# Production Deployment Guide

This guide provides step-by-step instructions to switch from local mock development environment back to production with real Chinese API and Render deployment.

## Overview

During local development, we set up a mock Chinese API server to simulate the real Chinese manufacturer API. This guide helps you revert all local changes and deploy to production.

## Current Local Development Setup

- Mock Chinese API server running on `http://localhost:8001`
- Local environment variables pointing to mock server
- Local SQLite database for development
- Mock authentication and payment simulation

## Step 1: Stop Local Development Services

```bash
# Stop all local servers
# Kill the mock Chinese API server (port 8001)
pkill -f "uvicorn.*8001"

# Stop the main API server (port 8000)
pkill -f "python api_server.py"

# Stop the frontend development server (port 5173)
pkill -f "npm run dev"
```

## Step 2: Environment Configuration Changes

### 2.1 Update .env.local for Production

Replace the contents of `.env.local` with production settings:

```bash
# Frontend API URL - Update to your Render API URL
VITE_API_BASE_URL=https://your-api-app.onrender.com

# Database Configuration - PRODUCTION
DATABASE_URL=postgresql://username:password@host:port/database

# OpenAI Configuration - PRODUCTION
OPENAI_API_KEY=your-actual-openai-api-key

# Chinese API Configuration - PRODUCTION
CHINESE_API_BASE_URL=https://production-chinese-api-url.com/mobileShell/en
CHINESE_API_ACCOUNT=your-production-account@email.com
CHINESE_API_PASSWORD=your-production-password
CHINESE_API_DEVICE_ID=your-production-device-id
CHINESE_API_TIMEOUT=30
```

### 2.2 Create .env for Production Deployment

Create a separate `.env` file for production deployment:

```bash
# Production Environment Variables
NODE_ENV=production
PORT=8000

# Database - Use your actual production database URL
DATABASE_URL=postgresql://username:password@host:port/database

# OpenAI API
OPENAI_API_KEY=your-actual-openai-api-key

# Chinese API - Real production endpoints
CHINESE_API_BASE_URL=https://production-chinese-api-url.com/mobileShell/en
CHINESE_API_ACCOUNT=your-production-account@email.com
CHINESE_API_PASSWORD=your-production-password
CHINESE_API_DEVICE_ID=your-production-device-id
CHINESE_API_TIMEOUT=30

# Stripe Configuration
STRIPE_SECRET_KEY=your-production-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-production-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=your-production-webhook-secret
```

## Step 3: Code Changes Review and Cleanup

### 3.1 Check api_routes.py Changes

During development, we made minimal changes to support the mock server. Review these changes:

```python
# In api_routes.py, line ~200
# This change was made to support mock server's uppercase "APPLE" format
"iphone": ["Apple", "APPLE", "苹果"]
```

**Decision**: Keep this change as it's backward compatible and handles both formats.

### 3.2 Remove Mock Server Dependencies (Optional)

If you want to completely remove mock server files:

```bash
# Remove the entire mock server directory
rm -rf chinese-api-mock/

# Remove mock-specific dependencies from requirements
# Edit requirements-api.txt and remove mock-only packages if any
```

**Recommendation**: Keep the mock server for future development needs.

## Step 4: Database Migration

### 4.1 Backup Current Database

```bash
# If using SQLite locally, backup the database
cp local_dev.db local_dev_backup.db
```

### 4.2 Configure Production Database

Update your database connection for production PostgreSQL:

```python
# Ensure your database URL format is correct
# postgresql://username:password@host:port/database_name
```

### 4.3 Run Database Migrations

```bash
# Install production dependencies
pip install -r requirements-api.txt

# Run any pending database migrations
python -c "
import db_services
db_services.init_db()
print('Database initialized successfully')
"
```

## Step 5: Frontend Production Build

### 5.1 Update Frontend Configuration

```bash
# Install dependencies
npm install

# Update the API base URL in .env.local
echo "VITE_API_BASE_URL=https://your-api-app.onrender.com" > .env.local
```

### 5.2 Build for Production

```bash
# Create production build
npm run build

# Test the production build locally (optional)
npm run preview
```

## Step 6: Deploy to Render

### 6.1 Backend Deployment (API Server)

1. **Create new Web Service on Render**:
   - Connect your GitHub repository
   - Select Python runtime
   - Set build command: `pip install -r requirements-api.txt`
   - Set start command: `python api_server.py`

2. **Environment Variables on Render**:
   ```
   NODE_ENV=production
   DATABASE_URL=your-postgresql-url
   OPENAI_API_KEY=your-openai-key
   CHINESE_API_BASE_URL=https://production-chinese-api.com/mobileShell/en
   CHINESE_API_ACCOUNT=your-production-account
   CHINESE_API_PASSWORD=your-production-password
   CHINESE_API_DEVICE_ID=your-production-device-id
   CHINESE_API_TIMEOUT=30
   STRIPE_SECRET_KEY=your-stripe-secret
   STRIPE_PUBLISHABLE_KEY=your-stripe-publishable
   STRIPE_WEBHOOK_SECRET=your-webhook-secret
   ```

3. **Deploy**: Trigger deployment from Render dashboard

### 6.2 Frontend Deployment (Static Site)

1. **Create new Static Site on Render**:
   - Connect your GitHub repository
   - Set build command: `npm run build`
   - Set publish directory: `dist`

2. **Environment Variables for Frontend**:
   ```
   VITE_API_BASE_URL=https://your-api-app.onrender.com
   ```

3. **Deploy**: Trigger deployment from Render dashboard

## Step 7: Production Testing

### 7.1 API Health Check

```bash
# Test your deployed API
curl https://your-api-app.onrender.com/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}
```

### 7.2 Chinese API Integration Test

```bash
# Test Chinese API connectivity
curl -X POST https://your-api-app.onrender.com/api/test-chinese-connection

# This should test:
# 1. Authentication with real Chinese API
# 2. Brand listing
# 3. Model retrieval
```

### 7.3 Frontend Integration Test

1. Visit your deployed frontend URL
2. Test the complete flow:
   - QR code generation (if applicable)
   - Brand selection
   - Model selection
   - Template selection
   - Image upload
   - AI generation
   - Payment processing
   - Order completion

## Step 8: Monitoring and Troubleshooting

### 8.1 Log Monitoring

Monitor Render logs for:
- API connection errors
- Chinese API authentication issues
- Database connection problems
- Payment processing errors

### 8.2 Common Issues and Solutions

**Chinese API Authentication Fails**:
```bash
# Check environment variables are set correctly
# Verify credentials with Chinese API provider
# Check API base URL format
```

**Database Connection Issues**:
```bash
# Verify DATABASE_URL format
# Check database permissions
# Ensure database is accessible from Render
```

**Payment Processing Fails**:
```bash
# Verify Stripe keys are production keys
# Check webhook endpoint configuration
# Ensure CORS is properly configured
```

## Step 9: Rollback Plan

If production deployment fails, you can quickly rollback to local development:

### 9.1 Restore Local Environment

```bash
# Restore local environment variables
git checkout .env.local

# Start mock servers
cd chinese-api-mock
python main.py &

# Start main API
python api_server.py &

# Start frontend
npm run dev
```

### 9.2 Database Rollback

```bash
# Restore local database
cp local_dev_backup.db local_dev.db
```

## Step 10: Post-Deployment Checklist

- [ ] Frontend loads correctly at production URL
- [ ] API health check passes
- [ ] Chinese API integration works
- [ ] Brand and model loading functions
- [ ] Image upload and AI generation work
- [ ] Payment processing functions correctly
- [ ] Order completion and status tracking work
- [ ] QR code generation works (if applicable)
- [ ] All environment variables are secure
- [ ] Database is properly configured
- [ ] Monitoring is in place

## Security Notes

1. **Never commit production credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate API keys** regularly
4. **Monitor API usage** and costs
5. **Implement rate limiting** if needed
6. **Use HTTPS** for all production endpoints

## Support Contacts

- **Chinese API Support**: [Provider contact information]
- **Render Support**: [Render documentation/support]
- **OpenAI Support**: [OpenAI documentation]
- **Stripe Support**: [Stripe documentation]

---

**Last Updated**: $(date)
**Author**: Development Team
**Version**: 1.0

This guide ensures a smooth transition from local mock development to production deployment while maintaining all functionality and security requirements.