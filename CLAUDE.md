# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend Development
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Backend Development
```bash
# Start the FastAPI server
python api_server.py

# Test API connection
python test_api_connection.py

# Install Python dependencies
pip install -r requirements-api.txt
```

## Architecture Overview

### Frontend Structure
- **React 18** with Vite build tool
- **Single Page Application** with React Router for navigation
- **Mobile-first** responsive design using Tailwind CSS
- **State Management** via React Context (`AppStateContext`)
- **Screen-based navigation** with 20+ screens handling the complete user flow

### Key Components
- **App.jsx**: Main routing configuration with all screen routes
- **AppStateContext**: Centralized state management with reducer pattern
- **Screen Components**: Individual screens for each step of the user journey
- **AI Service**: FastAPI backend integration for image generation

### User Flow Architecture
The app follows a linear vending machine flow:
```
QR → Brand → Model → Template → Upload → AI Generate → Text → Payment → Queue → Complete
```

### State Management
- **Centralized state** in `AppStateContext` with reducer pattern
- **Local storage persistence** for session recovery
- **QR session handling** for vending machine integration
- **Order status tracking** throughout the flow

### AI Integration
- **FastAPI backend** with OpenAI integration (GPT-image-1, DALL-E 3)
- **Chinese API integration** for phone case printing
- **Template system** with 5 AI-enhanced templates and 6 basic templates
- **Image generation service** with quality/size options

### Template System
- **Basic Templates**: Classic, 2-in-1, 3-in-1, 4-in-1, Film Strip
- **AI Templates**: Retro Remix, Cover Shoot, Funny Toon, Glitch Pro, Footy Fan
- **Dynamic requirements** based on selected template

### Font Management
- **Centralized font system** via `fontManager.js`
- **Fixed 30px font size** across the application
- **16 available fonts** including Google fonts

### Key Services
- **aiImageService.js**: Handles all AI generation and Chinese API communication
- **fontManager.js**: Centralized font definitions and styling
- **textBoundaryManager.js**: Text positioning and boundary management
- **imageEnhancer.js**: Image processing utilities

## Development Notes

### Environment Setup
- Frontend runs on port 5173 (Vite default)
- Backend runs on port 8000 (FastAPI)
- CORS configured for local development
- Environment variables: `VITE_API_BASE_URL` for API endpoint

### State Persistence
- State automatically persists to localStorage
- QR session parameters override saved state
- Loading and error states are not persisted

### API Integration
- Production API: `https://pimpmycase.onrender.com`
- Local development fallback available
- Chinese API integration for phone model data and order processing

### Mobile Optimization
- PWA ready with service worker and manifest
- Touch-optimized interface
- Responsive design for all screen sizes
- Offline capability through service worker