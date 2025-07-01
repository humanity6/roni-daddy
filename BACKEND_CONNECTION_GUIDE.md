# Backend Connection Guide

## Overview

This guide explains how the frontend React screens are connected to the FastAPI backend server for AI image generation.

## Architecture

```
Frontend (React) ↔ AI Service ↔ FastAPI Backend ↔ OpenAI API
```

### Components:

1. **Frontend Screens**: React components that handle user interactions
2. **AI Image Service**: Service layer that communicates with the backend
3. **FastAPI Backend**: API server that processes requests and calls OpenAI
4. **OpenAI API**: AI image generation service

## Connected Screens

### 1. Cover Shoot Generation
- **Setup Screen**: `CoverShootScreen.jsx`
- **Generate Screen**: `CoverShootGenerateScreen.jsx`
- **API Template**: `cover-shoot`
- **Styles**: Fashion, Glamour, Editorial, Portrait

### 2. Funny Toon Generation
- **Setup Screen**: `FunnyToonScreen.jsx`
- **Generate Screen**: `FunnyToonGenerateScreen.jsx`
- **API Template**: `funny-toon`
- **Styles**: Classic Cartoon, Anime Style, 3D Cartoon, Comic Book, Wild and Wacky

### 3. Retro Remix Generation
- **Setup Screen**: `RetroRemixScreen.jsx`
- **Generate Screen**: `RetroRemixGenerateScreen.jsx`
- **API Template**: `retro-remix`
- **Keywords**: Y2K Chrome, 80s Neon, 90s Grunge, Vaporwave

### 4. Glitch Pro Generation
- **Setup Screen**: `GlitchScreen.jsx`
- **Generate Screen**: `GlitchProGenerateScreen.jsx`
- **API Template**: `glitch-pro`
- **Modes**: Retro, Chaos, Neon, Matrix

### 5. Footy Fan Generation
- **Setup Screen**: `FootyFanScreen.jsx`
- **Style Screen**: `FootyFanStyleScreen.jsx`
- **Generate Screen**: `FootyFanGenerateScreen.jsx`
- **API Template**: `footy-fan`
- **Styles**: Team Colors, Stadium, Vintage, Modern

## API Service Layer

### Location: `src/services/aiImageService.js`

This service handles all communication between the frontend and backend:

```javascript
// Main generation method
async generateImage(templateId, styleParams, imageFile, quality, size)

// Template-specific methods
async generateCoverShoot(style, imageFile, quality)
async generateFunnyToon(style, imageFile, quality)
async generateRetroRemix(keyword, optionalText, imageFile, quality)
async generateGlitchPro(mode, imageFile, quality)
async generateFootyFan(team, style, imageFile, quality)
```

### Configuration

The service is configured to connect to:
- **Development**: `http://192.168.100.4:8000`
- **Local**: `http://localhost:8000`

Update the `API_BASE_URL` in `aiImageService.js` to match your backend server.

## Backend API Server

### Location: `api_server.py`

### Key Endpoints:

1. **Health Check**: `GET /health`
   - Checks API status and OpenAI connection
   
2. **Generate Image**: `POST /generate`
   - Generates AI images based on template and parameters
   
3. **Get Image**: `GET /image/{filename}`
   - Serves generated images
   
4. **Get Styles**: `GET /styles/{template_id}`
   - Returns available styles for a template

### Template Configuration

Each template has detailed prompts and style options defined in `STYLE_PROMPTS`:

```python
STYLE_PROMPTS = {
    "cover-shoot": {
        "base": "Professional magazine cover shoot...",
        "styles": {
            "Fashion": "high-fashion magazine cover...",
            "Glamour": "glamour photography style...",
            # ... more styles
        }
    },
    # ... other templates
}
```

## Setup Instructions

### 1. Backend Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements-api.txt
   ```

2. **Configure OpenAI API Key**:
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

3. **Start the API Server**:
   ```bash
   python api_server.py
   ```
   
   The server will run on `http://localhost:8000`

### 2. Frontend Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Update API URL** (if needed):
   Edit `src/services/aiImageService.js` and update `API_BASE_URL`

3. **Start the Frontend**:
   ```bash
   npm run dev
   ```

### 3. Test the Connection

Run the test script to verify connectivity:
```bash
python test_api_connection.py
```

## How It Works

### 1. User Flow

1. User selects a template (Cover Shoot, Funny Toon, etc.)
2. User uploads an image and adjusts positioning
3. User selects style options
4. User clicks "Generate" → Navigate to generate screen
5. Generate screen automatically starts AI generation
6. User can regenerate or proceed to next step

### 2. Technical Flow

1. **Image Upload**: User uploads image → Converted to base64 data URL
2. **Navigation**: Screen passes image and parameters via React Router state
3. **File Conversion**: Generate screen converts data URL back to File object
4. **API Call**: Service sends FormData with template, style params, and image file
5. **AI Generation**: Backend processes request and calls OpenAI API
6. **Response**: Generated image is saved and URL is returned
7. **Display**: Frontend displays the generated image

### 3. Error Handling

- **Network Errors**: Displayed to user with retry options
- **API Errors**: Specific error messages from backend
- **OpenAI Errors**: Fallback to DALL-E if GPT-image-1 unavailable
- **File Errors**: Validation and conversion error handling

## AI Credits System

Each generate screen includes:
- **Credit Counter**: Shows remaining AI credits
- **Credit Deduction**: Reduces credits on successful generation
- **Credit Validation**: Prevents generation when credits are exhausted

## Image Transform Controls

All generate screens include:
- **Zoom**: In/Out controls
- **Position**: Move image left/right/up/down
- **Reset**: Reset to default position and scale
- **Real-time Preview**: See changes immediately

## Debugging

### Common Issues:

1. **Connection Refused**: 
   - Check if API server is running
   - Verify API_BASE_URL is correct

2. **OpenAI API Errors**:
   - Check API key configuration
   - Verify API key has sufficient credits

3. **Image Processing Errors**:
   - Check image format and size
   - Verify file upload is working

### Debug Tools:

1. **Browser Console**: Check for JavaScript errors
2. **Network Tab**: Monitor API requests and responses
3. **Backend Logs**: Check Python console for errors
4. **Test Script**: Use `test_api_connection.py` for basic connectivity

## Customization

### Adding New Templates

1. **Backend**: Add new template to `STYLE_PROMPTS` in `api_server.py`
2. **Service**: Add new method to `aiImageService.js`
3. **Frontend**: Create new screen components
4. **Routing**: Add routes to `App.jsx`

### Modifying Styles

1. **Backend**: Update style options in `STYLE_PROMPTS`
2. **Frontend**: Update style selection UI in setup screens

### Changing Prompts

1. **Backend**: Modify prompt templates in `STYLE_PROMPTS`
2. **Testing**: Use test script to verify prompt generation

## Production Deployment

### Backend Considerations:
- Use environment variables for API keys
- Configure CORS for production domains
- Use a production WSGI server (gunicorn, uvicorn)
- Implement rate limiting and authentication

### Frontend Considerations:
- Update API_BASE_URL for production
- Build and serve static files
- Configure proper error boundaries
- Implement user authentication if needed

## Support

For issues or questions:
1. Check the console logs (both frontend and backend)
2. Run the test script to verify connectivity
3. Check the API health endpoint
4. Verify OpenAI API key configuration 