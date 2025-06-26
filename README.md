# Pimp My Case - Mobile Web App 📱

A modern mobile-first web application for custom phone case printing via vending machines.

## 🚀 Phase 1 & 2 Features

### Phase 1: Core Navigation
- **QR Code Welcome Screen** - Entry point for vending machine customers
- **Phone Brand Selection** - Choose between iPhone, Samsung, and Google (coming soon)
- **Phone Model & Color Selection** - Select specific device model and color
- **Phone Case Preview** - Real-time preview with image upload capability

### Phase 2: Template System
- **Template Selection Screen** - 11 different design modes with visual previews
- **Basic Templates (4)** - Classic, 2-in-1, 3-in-1, 4-in-1 layouts
- **Film Strip Templates (2)** - Vintage film strip layouts for multiple images
- **AI-Enhanced Templates (5)** - Retro Remix, Cover Shoot, Funny Toon, Glitch Pro, Footy Fan
- **Phone Back Preview** - Real-time template application with multi-image support
- **Smart Upload System** - Dynamic image requirements based on selected template

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Tailwind CSS** - Mobile-first responsive design
- **Lucide React** - Beautiful icons

## 📱 Mobile-First Design

- Touch-friendly interactions
- Smooth animations and transitions
- Responsive layouts optimized for mobile screens
- PWA-ready with proper viewport settings

## 🎯 Getting Started

### Prerequisites

- Node.js 16 or higher
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:5173](http://localhost:5173) in your browser

### Build for Production

```bash
npm run build
```

## 🗺️ Navigation Flow

```
Welcome Screen → Phone Brand → Phone Model → Preview
     ↓              ↓            ↓           ↓
 QR Code Entry → iPhone/Samsung → Model+Color → Upload Image
```

## 🎨 Design System

- **Primary Colors**: Pink gradient (`from-pink-500 to-rose-500`)
- **Typography**: Inter font family
- **Animations**: Fade-in, slide-up, scale effects
- **Components**: Reusable button styles and mobile containers

## 📦 Project Structure

```
src/
├── screens/          # Main app screens
│   ├── WelcomeScreen.jsx
│   ├── PhoneBrandScreen.jsx
│   ├── PhoneModelScreen.jsx
│   └── PhonePreviewScreen.jsx
├── App.jsx          # Main app with routing
├── main.jsx         # React entry point
└── index.css        # Global styles with Tailwind

public/              # Static assets
ui-mockups/          # Design reference images
```

## ✅ Phase 4: Complete Order Flow (NEW)

### Final Production Screens
- **RetryScreen** - Design modification interface with AI enhancement options
- **PaymentScreen** - £17.99 payment processing with card reader integration
- **QueueScreen** - Real-time queue status with animated progress indicators
- **CompletionScreen** - "ORDER CONFIRMED!" with order number display

### State Management System
- **Global Context** - Complete app state management with persistence
- **QR Session Handling** - URL parameter processing for kiosk integration
- **LocalStorage Persistence** - Session continuity across page reloads

### Progressive Web App (PWA)
- **Service Worker** - Offline functionality and caching
- **Web App Manifest** - Installable on mobile devices
- **Push Notifications** - Order status updates
- **Mobile Optimization** - Full PWA compliance

## 🔄 Project Status

- **Phase 1** ✅ - Basic navigation and phone selection
- **Phase 2** ✅ - Template selection with 11 design modes  
- **Phase 3** ✅ - Text customization and font selection
- **Phase 4** ✅ - Complete order flow and PWA features

## 📱 Complete User Journey

```
Welcome → Brand → Model → Template → Preview → Text → Font → Color
    ↓
BackPreview → Retry → Payment → Queue → Completion
```

## 🛠️ Production Ready Features

- ✅ Complete end-to-end user flow
- ✅ State persistence and error handling
- ✅ PWA with offline capabilities
- ✅ Mobile-optimized touch interface
- ✅ Loading states and smooth animations
- ✅ QR code session parameter handling
- ✅ Production-ready build system

## 🎯 API Integration Points

The app is ready for backend integration with clearly defined state management for:
- Payment processing endpoints
- Order submission and tracking
- Queue position updates
- Print job status monitoring

---

**Status: PRODUCTION READY** - Complete mobile web app ready for deployment and API integration

Built with ❤️ for modern mobile experiences 