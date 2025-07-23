# Hostinger Git Integration Setup

Since FTP is having issues, let's use Hostinger's native Git integration instead.

## Method 1: Hostinger Git Integration (Recommended)

### Step 1: Setup Mobile App Git Integration

1. **In Hostinger hPanel:**
   - Go to **Websites** → **Manage** (for pimpmycase.shop)
   - Look for **Git** in the left sidebar (under Advanced)
   - Click **Git**

2. **Connect Repository:**
   - Click **Create new repository** or **Connect repository**
   - Enter your GitHub repository URL: `https://github.com/humanity6/roni-daddy`
   - Branch: `main`
   - Deployment path: `/domains/pimpmycase.shop/public_html/`
   - Build command: `npm ci && npm run build`
   - Publish directory: `dist`

3. **Auto-Deployment:**
   - Enable **Auto Deployment**
   - Copy the webhook URL provided
   - Go to your GitHub repo → **Settings** → **Webhooks**
   - Add new webhook with the URL from Hostinger

### Step 2: Setup Admin Dashboard Git Integration

1. **Create Subdomain First:**
   - In hPanel → **Subdomains**
   - Create: `admin.pimpmycase.shop`
   - Point to: `/domains/pimpmycase.shop/public_html/admin/`

2. **Setup Git for Admin:**
   - Go to **Websites** → **Manage** (for admin.pimpmycase.shop)
   - Follow same Git setup process
   - Repository: Same GitHub repo
   - Branch: `main`
   - Deployment path: `/domains/pimpmycase.shop/public_html/admin/`
   - Build command: `cd admin-dashboard && npm ci && npm run build`
   - Publish directory: `admin-dashboard/dist`

## Method 2: Manual File Upload (Quick Fix)

If Git integration doesn't work immediately:

### For Mobile App:
1. Run locally: `npm run build`
2. Download the `dist` folder contents
3. In Hostinger hPanel → **File Manager**
4. Navigate to `/domains/pimpmycase.shop/public_html/`
5. Upload all files from `dist` folder

### For Admin Dashboard:
1. Run locally: `cd admin-dashboard && npm run build`
2. Download the `admin-dashboard/dist` folder contents
3. In Hostinger File Manager
4. Navigate to `/domains/pimpmycase.shop/public_html/admin/`
5. Upload all files from `admin-dashboard/dist` folder

## Method 3: Fix FTP (Alternative)

If you want to continue with FTP, try these FTP settings:

**Common Hostinger FTP hosts to try:**
- `ftp.hostinger.com`
- `ftp.hostinger.net`
- `82.29.189.39` (your server IP)
- `files.hostinger.com`

**Port:** Usually 21 (or try 22 for SFTP)

## Verification

After deployment, check:
- **Mobile App**: https://pimpmycase.shop
- **Admin Dashboard**: https://admin.pimpmycase.shop

## Next Steps

1. **Try Hostinger Git integration first** (most reliable)
2. **Manual upload** if you need immediate deployment
3. **Fix FTP** as a last resort

The Git integration method is most reliable and gives you automatic deployment without GitHub Actions complications.