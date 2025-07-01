# Quick Start Guide - Fix Connection Issues

## 🚨 If you're getting connection errors, follow these steps:

### Step 1: Start the API Server

**Option A: Using the batch script (Windows)**
```bash
start_api_server.bat
```

**Option B: Manual start**
```bash
# 1. Install dependencies
pip install fastapi uvicorn openai pillow python-dotenv

# 2. Create .env file with your OpenAI API key
echo OPENAI_API_KEY=sk-your-actual-key-here > .env

# 3. Start the server
python api_server.py
```

### Step 2: Verify API Server is Running

1. **Check the console output** - You should see:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   INFO:     Application startup complete.
   ```

2. **Test the health endpoint** in your browser:
   ```
   http://localhost:8000/health
   ```
   You should see a JSON response with status information.

3. **Run the connection test**:
   ```bash
   python test_api_connection.py
   ```

### Step 3: Common Connection Issues

#### Issue: "ERR_CONNECTION_TIMED_OUT"
**Solutions:**
- Make sure the API server is actually running
- Check if port 8000 is available (close other applications using it)
- Try restarting the API server
- Check Windows Firewall settings

#### Issue: "CORS Error"
**Solutions:**
- The API server includes CORS configuration for localhost
- Make sure you're accessing the frontend from `http://localhost:5173`

#### Issue: "OpenAI API Key Error"
**Solutions:**
- Create a `.env` file in the root directory
- Add your OpenAI API key: `OPENAI_API_KEY=sk-your-actual-key-here`
- Make sure the key starts with `sk-` and is valid

### Step 4: Test the Full Flow

1. **Start both servers:**
   ```bash
   # Terminal 1: API Server
   python api_server.py

   # Terminal 2: Frontend
   npm run dev
   ```

2. **Open the app:**
   ```
   http://localhost:5173
   ```

3. **Test AI generation:**
   - Go through the flow to Cover Shoot
   - Upload an image
   - Click "Generate" 
   - Should navigate to generate screen and start AI processing

### Step 5: Debug Information

If you're still having issues, check:

1. **Browser Console (F12):**
   - Look for network errors
   - Check if API requests are being made to the correct URL

2. **API Server Console:**
   - Check for Python errors
   - Verify OpenAI API calls are working

3. **Network Tab:**
   - Monitor API requests
   - Check response codes and error messages

### Emergency Troubleshooting

If nothing works:

1. **Clear browser cache and service worker:**
   ```javascript
   // In browser console:
   navigator.serviceWorker.getRegistrations().then(function(registrations) {
     for(let registration of registrations) {
       registration.unregister();
     }
   });
   ```

2. **Restart everything:**
   - Close all terminals
   - Restart API server
   - Restart frontend dev server
   - Refresh browser

3. **Check API URL:**
   - In `src/services/aiImageService.js`
   - Make sure `API_BASE_URL` is `http://localhost:8000`

### Success Indicators

✅ **API Server Running:** Console shows "Uvicorn running on http://0.0.0.0:8000"
✅ **Health Check:** `http://localhost:8000/health` returns JSON
✅ **Frontend Connected:** No CORS or connection errors in browser console
✅ **AI Generation:** Generate screens show "Generating..." then display AI images

Need more help? Check the detailed [Backend Connection Guide](BACKEND_CONNECTION_GUIDE.md). 