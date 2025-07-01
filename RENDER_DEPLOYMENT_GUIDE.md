# Render.com Deployment Guide for Pimp My Case API

## Quick Start Checklist

✅ **Step 1:** Push code to GitHub (including `render.yaml`)  
✅ **Step 2:** Create Render service from GitHub repo  
✅ **Step 3:** Add `OPENAI_API_KEY` environment variable in Render  
✅ **Step 4:** Get your API URL from Render dashboard  
✅ **Step 5:** Add `VITE_API_BASE_URL` to Vercel environment variables  
✅ **Step 6:** Redeploy your Vercel frontend  
✅ **Step 7:** Test the connection!  

## Prerequisites
- GitHub repository with your code
- OpenAI API key
- Render.com account

## Deployment Methods

### Method 1: Using render.yaml (Recommended)

1. **Push your code to GitHub** including the `render.yaml` file
2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Sign up/Login with GitHub
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository containing your code

3. **Configure Environment Variables:**
   - After deployment starts, go to your service dashboard
   - Navigate to "Environment" tab
   - Add your OpenAI API key:
     - Key: `OPENAI_API_KEY`
     - Value: `your-actual-openai-api-key`

### Method 2: Manual Web Service Setup

1. **Create New Web Service:**
   - Go to Render dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service Settings:**
   ```
   Name: pimp-my-case-api
   Runtime: Python 3
   Build Command: pip install -r requirements-api.txt
   Start Command: uvicorn api_server:app --host 0.0.0.0 --port $PORT
   ```

3. **Set Environment Variables:**
   - Add `OPENAI_API_KEY` with your actual API key

## Important Notes

### File Structure
Make sure these files are in your repository root:
- `api_server.py` (your main FastAPI app)
- `requirements-api.txt` (Python dependencies)
- `render.yaml` (deployment configuration)

### Environment Variables
Your OpenAI API key will be set in Render's dashboard:
- Go to your service → Environment tab
- Add: `OPENAI_API_KEY = sk-your-actual-key-here`

### CORS Configuration
Your API is already configured to accept requests from:
- `https://pimp-my-case.vercel.app` (Production)
- `https://pimp-my-case-git-main-arshads-projects-c0bbf026.vercel.app` (Git branch)
- `https://pimp-my-case-nh7bek7vb-arshads-projects-c0bbf026.vercel.app` (Preview)
- Local development ports

### Generated Images Storage
- Render's free tier has ephemeral storage
- Generated images will be lost on service restarts
- Consider upgrading to a paid plan or using external storage (S3, Cloudinary) for production

## Testing Your Deployment

1. **Get your API URL:**
   - ✅ **Your deployed API URL:** `https://pimpmycase.onrender.com`

2. **Test the health endpoint:**
   ```bash
   curl https://pimpmycase.onrender.com/health
   ```

3. **Update your frontend:**
   - Update your Vercel frontend to use the Render API URL
   - Replace any localhost API calls with your production API URL

## Frontend Integration

Your frontend is already configured to use environment variables for the API URL. After your Render API is deployed:

### Update Vercel Environment Variables:

1. **Go to your Vercel dashboard:**
   - Navigate to your project: `pimp-my-case`
   - Go to Settings → Environment Variables

2. **Add the production API URL:**
   ```
   Variable Name: VITE_API_BASE_URL
   Value: https://pimpmycase.onrender.com
   ```
   ✅ **Your actual Render API URL:** `https://pimpmycase.onrender.com`

3. **Redeploy your frontend:**
   - Go to Deployments tab
   - Click "Redeploy" on your latest deployment
   - Or push a new commit to trigger automatic deployment

### Local Development:
Create a `.env.local` file in your frontend root:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Environment Configuration:
Your frontend now automatically uses:
- Production API URL when deployed on Vercel
- Local API URL when developing locally

## Troubleshooting

### Common Issues:
1. **Build Fails:** Check that `requirements-api.txt` includes all dependencies
2. **Service Won't Start:** Verify the start command uses `$PORT` environment variable
3. **CORS Errors:** Ensure your Vercel domain is in the CORS allow_origins list
4. **API Key Issues:** Double-check your OpenAI API key in environment variables

### Logs:
- View deployment logs in Render dashboard
- Use the "Logs" tab to debug any issues

## Production Considerations

1. **Upgrade Plan:** Free tier sleeps after inactivity (may cause delays)
2. **Database:** Add PostgreSQL if you need persistent data storage
3. **File Storage:** Use external storage for generated images
4. **Monitoring:** Set up health checks and alerts
5. **Custom Domain:** Configure custom domain if needed

## Security
- Never commit API keys to version control
- Use environment variables for all sensitive data
- Enable HTTPS (automatic on Render) 