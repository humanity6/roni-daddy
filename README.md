# Pimp My Case - Mobile Web App 📱

A modern mobile-first web application for custom phone case printing via vending machines with AI-powered image generation.

## 🚀 Features

### Core Navigation
- **QR Code Welcome Screen** - Entry point for vending machine customers
- **Phone Brand Selection** - Choose between iPhone, Samsung, and Google (coming soon)
- **Phone Model & Color Selection** - Select specific device model and color
- **Phone Case Preview** - Real-time preview with image upload capability

### Template System
- **Template Selection Screen** - 11 different design modes with visual previews
- **Basic Templates (4)** - Classic, 2-in-1, 3-in-1, 4-in-1 layouts
- **Film Strip Templates (2)** - Vintage film strip layouts for multiple images
- **AI-Enhanced Templates (5)** - Retro Remix, Cover Shoot, Funny Toon, Glitch Pro, Footy Fan
- **Phone Back Preview** - Real-time template application with multi-image support
- **Smart Upload System** - Dynamic image requirements based on selected template

### AI Image Generation 🤖
- **FastAPI Backend** - High-performance API server for AI processing
- **OpenAI Integration** - GPT-image-1 and DALL-E 3 support
- **Real-time Generation** - Live AI image processing with progress feedback
- **Multiple Styles** - Each template offers various artistic styles
- **Credit System** - Built-in AI credit management and tracking

### Complete Order Flow
- **RetryScreen** - Design modification interface with AI enhancement options
- **PaymentScreen** - £17.99 payment processing with card reader integration
- **QueueScreen** - Real-time queue status with animated progress indicators
- **CompletionScreen** - "ORDER CONFIRMED!" with order number display

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Mobile-first responsive design
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - Modern, fast web framework for Python
- **OpenAI API** - AI image generation (GPT-image-1, DALL-E 3)
- **Pillow** - Image processing and optimization
- **uvicorn** - ASGI server for production

## 🎯 Getting Started

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:5173](http://localhost:5173) in your browser

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements-api.txt
```

2. Configure OpenAI API key:
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

3. Start the API server:
```bash
python api_server.py
```
Or use the Windows batch script:
```bash
start_api_server.bat
```

4. Test the connection:
```bash
python test_api_connection.py
```

### Build for Production

```bash
npm run build
```

## 🤖 AI Templates & Styles

### 1. Cover Shoot
Professional magazine-style photography
- **Styles**: Fashion, Glamour, Editorial, Portrait

### 2. Funny Toon
Cartoon character transformations
- **Styles**: Classic Cartoon, Anime Style, 3D Cartoon, Comic Book, Wild and Wacky

### 3. Retro Remix
Vintage aesthetic transformations
- **Keywords**: Y2K Chrome, 80s Neon, 90s Grunge, Vaporwave

### 4. Glitch Pro
Digital glitch effects
- **Modes**: Retro, Chaos, Neon, Matrix

### 5. Footy Fan
Sports fan artwork
- **Styles**: Team Colors, Stadium, Vintage, Modern

## 🗺️ Navigation Flow

```
Welcome → Brand → Model → Template → Preview → AI Generation → Text → Payment → Queue → Complete
```

## 📦 Project Structure

```
src/
├── screens/          # Main app screens
│   ├── AI Generation/
│   │   ├── CoverShootScreen.jsx
│   │   ├── CoverShootGenerateScreen.jsx
│   │   ├── FunnyToonGenerateScreen.jsx
│   │   ├── RetroRemixGenerateScreen.jsx
│   │   ├── GlitchProGenerateScreen.jsx
│   │   └── FootyFanGenerateScreen.jsx
│   └── [other screens...]
├── services/
│   └── aiImageService.js    # AI API communication
├── components/              # Reusable components
├── contexts/               # React Context providers
└── utils/                  # Utility functions

Backend/
├── api_server.py           # FastAPI server
├── test_api_connection.py  # Connection test script
├── start_api_server.bat    # Windows startup script
└── requirements-api.txt    # Python dependencies
```

## 🔧 API Endpoints

- `GET /health` - Health check and OpenAI connection status
- `POST /generate` - AI image generation
- `GET /image/{filename}` - Serve generated images
- `GET /styles/{template_id}` - Get available styles for template

## 🎨 Design System

- **Primary Colors**: Pink gradient (`from-pink-500 to-rose-500`)
- **Typography**: Inter font family
- **Animations**: Fade-in, slide-up, scale effects
- **Components**: Reusable button styles and mobile containers

## 🔄 Development Status

- **Phase 1** ✅ - Basic navigation and phone selection
- **Phase 2** ✅ - Template selection with 11 design modes  
- **Phase 3** ✅ - Text customization and font selection
- **Phase 4** ✅ - Complete order flow and PWA features
- **Phase 5** ✅ - AI Backend Integration

## 📱 Progressive Web App (PWA)

- **Service Worker** - Offline functionality and caching
- **Web App Manifest** - Installable on mobile devices
- **Push Notifications** - Order status updates
- **Mobile Optimization** - Full PWA compliance

## 🛠️ Production Ready Features

- ✅ Complete end-to-end user flow
- ✅ AI-powered image generation
- ✅ State persistence and error handling
- ✅ PWA with offline capabilities
- ✅ Mobile-optimized touch interface
- ✅ Loading states and smooth animations
- ✅ QR code session parameter handling
- ✅ Production-ready build system
- ✅ FastAPI backend with OpenAI integration

## 📚 Documentation

- **[Backend Connection Guide](BACKEND_CONNECTION_GUIDE.md)** - Detailed setup and troubleshooting
- **[API Documentation](api_server.py)** - FastAPI server implementation
- **[Test Scripts](test_api_connection.py)** - Connection testing utilities

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure API server is running on port 8000
   - Check `API_BASE_URL` in `aiImageService.js`
   - Verify OpenAI API key configuration

2. **Image Generation Errors**
   - Check OpenAI API key validity and credits
   - Verify image file format and size
   - Check browser console for detailed errors

3. **CORS Issues**
   - Ensure frontend URL is in CORS allowed origins
   - Check network configuration for local development

### Debug Tools

- Browser DevTools → Console for frontend errors
- Network tab for API request monitoring
- Python console for backend logs
- `test_api_connection.py` for connectivity verification

---

**Status: PRODUCTION READY WITH AI** - Complete mobile web app with AI image generation ready for deployment

Built with ❤️ for modern mobile experiences and powered by AI 🤖 