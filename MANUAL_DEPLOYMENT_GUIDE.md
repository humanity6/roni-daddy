# Manual Deployment Guide

Since Hostinger Git integration is having issues, here's a quick manual deployment method:

## Quick Manual Deployment

### Step 1: Build Locally

**Mobile App:**
```bash
npm ci
npm run build
```

**Admin Dashboard:**
```bash
cd admin-dashboard
npm ci
npm run build
cd ..
```

### Step 2: Upload via Hostinger File Manager

1. **Login to Hostinger hPanel**
2. **Go to Files → File Manager**
3. **Navigate to `/domains/pimpmycase.shop/public_html/`**

**For Mobile App:**
4. **Delete all existing files** in `/public_html/` 
5. **Upload all files from `dist/` folder** to `/public_html/`

**For Admin Dashboard:**
6. **Create folder:** `/public_html/admin/` (if it doesn't exist)
7. **Upload all files from `admin-dashboard/dist/` folder** to `/public_html/admin/`

### Step 3: Verify Deployment

- **Mobile App**: Visit `https://pimpmycase.shop`
- **Admin Dashboard**: Visit `https://admin.pimpmycase.shop`

## Alternative: Use Hostinger File Manager Upload

1. **Zip your dist folders:**
   - `dist.zip` (mobile app)
   - `admin-dist.zip` (admin dashboard)

2. **Upload via File Manager:**
   - Upload and extract `dist.zip` to `/public_html/`
   - Upload and extract `admin-dist.zip` to `/public_html/admin/`

This method will get your sites live immediately while we troubleshoot the Git integration.