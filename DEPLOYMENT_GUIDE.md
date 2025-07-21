# 🚀 Complete Deployment Guide: Vercel + Render

This guide covers deploying your entire PimpMyCase application stack using only **Vercel** and **Render**.

## 📋 Architecture Overview

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend (Vercel) │    │  Backend (Render)   │    │  Database (Render)  │
│                     │    │                     │    │                     │
│ • React Web App     │────│ • FastAPI Server    │────│ • PostgreSQL        │
│ • Admin Dashboard   │    │ • AI Integration    │    │ • File Storage      │
│ • Static Assets     │    │ • Stripe Webhooks   │    │ • Image Storage     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

---

## 🗄️ Step 1: Database Setup on Render

### 1.1 Create PostgreSQL Database

1. **Go to Render Dashboard** → https://dashboard.render.com
2. **Click "New"** → **"PostgreSQL"**
3. **Configure Database:**
   ```
   Name: pimpmycase-database
   Database: pimpmycase_db
   User: pimpmycase_user
   Region: Oregon (US West) or Frankfurt (EU Central)
   PostgreSQL Version: 15
   Plan: Starter ($7/month) or Free (limited)
   ```

4. **Save Connection Details:**
   ```
   Internal Database URL: postgresql://username:password@hostname:port/database
   External Database URL: postgresql://username:password@hostname:port/database
   ```

### 1.2 Initialize Database Schema

**Create `init_database.sql`:**
```sql
-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Customer info
    customer_email VARCHAR(255),
    customer_phone VARCHAR(50),
    
    -- Product details
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    color VARCHAR(50),
    template_id VARCHAR(100) NOT NULL,
    template_name VARCHAR(200),
    
    -- Design
    design_image_url TEXT,
    custom_text TEXT,
    font_family VARCHAR(100),
    text_color VARCHAR(50),
    
    -- Pricing
    base_price DECIMAL(10,2),
    total_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    
    -- Payment
    stripe_session_id VARCHAR(255),
    stripe_payment_intent_id VARCHAR(255),
    payment_status VARCHAR(50) DEFAULT 'pending',
    
    -- Order status
    order_status VARCHAR(50) DEFAULT 'processing',
    queue_position INTEGER,
    
    -- Chinese API integration
    chinese_order_id VARCHAR(255),
    chinese_status VARCHAR(100),
    tracking_number VARCHAR(255),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- AI generations table
CREATE TABLE IF NOT EXISTS ai_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    template_id VARCHAR(100) NOT NULL,
    style_params JSONB NOT NULL,
    quality VARCHAR(20) DEFAULT 'low',
    image_size VARCHAR(20) DEFAULT '1024x1536',
    
    original_image_url TEXT,
    generated_image_url TEXT,
    generation_time_ms INTEGER,
    
    cost_estimate DECIMAL(10,4),
    tokens_used INTEGER,
    
    success BOOLEAN DEFAULT false,
    error_message TEXT,
    
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Admin users table
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    role VARCHAR(50) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    
    permissions JSONB DEFAULT '["read", "write"]'::jsonb
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON orders(payment_status);
CREATE INDEX IF NOT EXISTS idx_orders_stripe_session ON orders(stripe_session_id);
CREATE INDEX IF NOT EXISTS idx_ai_generations_created_at ON ai_generations(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_generations_template ON ai_generations(template_id);

-- Insert default admin user (change password in production!)
INSERT INTO admin_users (username, email, password_hash) 
VALUES ('admin', 'admin@pimpmycase.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeVMsteww') 
ON CONFLICT (username) DO NOTHING;
```

**Run the schema:**
```bash
# Connect to your Render PostgreSQL database
psql "postgresql://username:password@hostname:port/database" -f init_database.sql
```

---

## 🖥️ Step 2: Backend Deployment on Render

### 2.1 Prepare Backend for Deployment

**Update `requirements-api.txt`:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
Pillow==10.1.0
openai==1.3.7
stripe==7.8.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.13.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2
boto3==1.34.0
sentry-sdk[fastapi]==1.38.0
```

**Create Production-Ready `api_server.py`:**
```python
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import asyncio
import uvicorn

from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import stripe
import openai
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, DECIMAL, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid
from passlib.context import CryptContext
from jose import JWTError, jwt
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Initialize Sentry for error tracking
if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="PimpMyCase API",
    description="AI-powered phone case customization API",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",  # Replace with your frontend URL
        "https://your-admin.vercel.app",     # Replace with your admin URL
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize external services
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Database Models
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Customer info
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    
    # Product details
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    color = Column(String(50))
    template_id = Column(String(100), nullable=False)
    template_name = Column(String(200))
    
    # Design
    design_image_url = Column(Text)
    custom_text = Column(Text)
    font_family = Column(String(100))
    text_color = Column(String(50))
    
    # Pricing
    base_price = Column(DECIMAL(10, 2))
    total_price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='GBP')
    
    # Payment
    stripe_session_id = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    payment_status = Column(String(50), default='pending')
    
    # Order status
    order_status = Column(String(50), default='processing')
    queue_position = Column(Integer)
    
    # Chinese API integration
    chinese_order_id = Column(String(255))
    chinese_status = Column(String(100))
    tracking_number = Column(String(255))
    
    # Metadata
    metadata = Column(JSON, default={})

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    role = Column(String(50), default='admin')
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    
    permissions = Column(JSON, default=["read", "write"])

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    return user

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "production"),
        "services": {
            "database": "connected" if DATABASE_URL else "not_configured",
            "stripe": "configured" if stripe.api_key else "not_configured",
            "openai": "configured" if openai.api_key else "not_configured"
        }
    }

# Authentication endpoints
@app.post("/admin/login")
async def admin_login(credentials: dict, db: Session = Depends(get_db)):
    username = credentials.get("username")
    password = credentials.get("password")
    
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "permissions": user.permissions
        }
    }

# Admin endpoints
@app.get("/admin/dashboard")
async def admin_dashboard(current_user: AdminUser = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get dashboard statistics
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.order_status == 'processing').count()
    completed_orders = db.query(Order).filter(Order.order_status == 'completed').count()
    
    return {
        "stats": {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders
        },
        "recent_orders": []  # Add recent orders query here
    }

@app.get("/admin/orders")
async def get_orders(
    skip: int = 0, 
    limit: int = 50,
    status: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    query = db.query(Order)
    if status:
        query = query.filter(Order.order_status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return {"orders": orders}

# Stripe payment endpoints
@app.post("/create-checkout-session")
async def create_checkout_session(request_data: dict, db: Session = Depends(get_db)):
    try:
        # Create order in database first
        order = Order(
            brand=request_data.get('brand'),
            model=request_data.get('model'),
            color=request_data.get('color'),
            template_id=request_data.get('template_id'),
            template_name=request_data.get('template_name'),
            design_image_url=request_data.get('design_image_url'),
            custom_text=request_data.get('custom_text'),
            total_price=request_data.get('price', 0),
            metadata=request_data
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': f'Phone Case - {request_data.get("template_name", "Custom")}',
                        'description': f'{request_data.get("brand")} {request_data.get("model")}',
                        'images': [request_data.get("design_image_url")] if request_data.get("design_image_url") else [],
                    },
                    'unit_amount': int(float(request_data.get("price", 0)) * 100),  # Convert to pence
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'https://your-frontend.vercel.app/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='https://your-frontend.vercel.app/payment',
            metadata={
                'order_id': str(order.id),
                'brand': request_data.get('brand'),
                'model': request_data.get('model'),
            }
        )
        
        # Update order with Stripe session ID
        order.stripe_session_id = checkout_session.id
        db.commit()
        
        return {"checkout_url": checkout_session.url, "order_id": str(order.id)}
        
    except Exception as e:
        logger.error(f"Checkout session creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/process-payment-success")
async def process_payment_success(request_data: dict, db: Session = Depends(get_db)):
    try:
        session_id = request_data.get('session_id')
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")
        
        # Retrieve the Stripe session
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status != 'paid':
            raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Find the order
        order = db.query(Order).filter(Order.stripe_session_id == session_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update order status
        order.payment_status = 'paid'
        order.stripe_payment_intent_id = session.payment_intent
        order.order_status = 'paid'
        order.updated_at = datetime.utcnow()
        
        # Generate queue number for display
        queue_no = f"Q{str(order.created_at.timestamp())[-6:]}"
        
        db.commit()
        
        return {
            "success": True,
            "order_id": str(order.id),
            "payment_id": session.payment_intent,
            "queue_no": queue_no,
            "status": "paid"
        }
        
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order = db.query(Order).filter(Order.stripe_session_id == session['id']).first()
        if order:
            order.payment_status = 'paid'
            order.order_status = 'paid'
            db.commit()
            logger.info(f"Order {order.id} payment confirmed via webhook")
    
    return {"status": "success"}

# AI Generation endpoints (your existing AI code here)
@app.post("/generate")
async def generate_image(
    template_id: str = Form(...),
    style_params: str = Form(...),
    quality: str = Form(default="low"),
    size: str = Form(default="1024x1536"),
    image: Optional[UploadFile] = File(None)
):
    # Your existing AI generation logic here
    # This is a placeholder - implement your actual AI generation
    return {
        "success": True,
        "filename": "generated_image.png",
        "message": "Image generated successfully"
    }

@app.get("/image/{filename}")
async def get_image(filename: str):
    # Serve generated images
    # This is a placeholder - implement your actual image serving
    image_path = f"generated-images/{filename}"
    if os.path.exists(image_path):
        return FileResponse(image_path)
    raise HTTPException(status_code=404, detail="Image not found")

# Static files for admin dashboard (if serving from same domain)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
```

### 2.2 Deploy to Render

1. **Connect GitHub Repository:**
   - Go to Render Dashboard → "New" → "Web Service"
   - Connect your GitHub repository
   - Select your backend directory

2. **Configure Web Service:**
   ```
   Name: pimpmycase-api
   Environment: Python 3
   Build Command: pip install -r requirements-api.txt
   Start Command: python api_server.py
   Plan: Starter ($7/month) or Free (limited)
   ```

3. **Environment Variables:**
   ```
   DATABASE_URL=<from_step_1>
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   OPENAI_API_KEY=sk-...
   JWT_SECRET_KEY=your-super-secret-jwt-key
   ENVIRONMENT=production
   SENTRY_DSN=https://...@sentry.io/... (optional)
   ```

4. **Deploy and Note URL:**
   - Your API will be available at: `https://pimpmycase-api.onrender.com`

---

## 🌐 Step 3: Frontend Deployment on Vercel

### 3.1 Main Frontend App

1. **Prepare for Deployment:**
   
   **Update `package.json`:**
   ```json
   {
     "name": "pimpmycase-frontend",
     "scripts": {
       "dev": "vite",
       "build": "vite build",
       "preview": "vite preview",
       "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
     },
     "dependencies": {
       "react": "^18.2.0",
       "react-dom": "^18.2.0",
       "react-router-dom": "^6.8.0",
       "@stripe/stripe-js": "^2.1.0",
       "lucide-react": "^0.263.1"
     }
   }
   ```

   **Create `vercel.json`:**
   ```json
   {
     "name": "pimpmycase-frontend",
     "version": 2,
     "builds": [
       {
         "src": "package.json",
         "use": "@vercel/static-build",
         "config": {
           "distDir": "dist"
         }
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "/index.html"
       }
     ],
     "env": {
       "VITE_API_BASE_URL": "https://pimpmycase-api.onrender.com",
       "VITE_STRIPE_PUBLISHABLE_KEY": "pk_live_..."
     }
   }
   ```

2. **Deploy to Vercel:**
   ```bash
   # Install Vercel CLI
   npm install -g vercel

   # Login to Vercel
   vercel login

   # Deploy from frontend directory
   cd frontend
   vercel

   # For production deployment
   vercel --prod
   ```

3. **Set Environment Variables in Vercel Dashboard:**
   - Go to your project → Settings → Environment Variables
   - Add:
     ```
     VITE_API_BASE_URL=https://pimpmycase-api.onrender.com
     VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...
     ```

### 3.2 Admin Dashboard Deployment

1. **Prepare Admin Dashboard:**
   
   **Create `admin-dashboard/package.json`:**
   ```json
   {
     "name": "pimpmycase-admin",
     "scripts": {
       "dev": "vite",
       "build": "vite build",
       "preview": "vite preview"
     },
     "dependencies": {
       "react": "^18.2.0",
       "react-dom": "^18.2.0",
       "react-router-dom": "^6.8.0",
       "axios": "^1.6.0",
       "recharts": "^2.8.0",
       "lucide-react": "^0.263.1"
     },
     "devDependencies": {
       "@types/react": "^18.2.15",
       "@types/react-dom": "^18.2.7",
       "@vitejs/plugin-react": "^4.0.3",
       "vite": "^4.4.5"
     }
   }
   ```

   **Create `admin-dashboard/src/main.jsx`:**
   ```jsx
   import React from 'react'
   import ReactDOM from 'react-dom/client'
   import { BrowserRouter } from 'react-router-dom'
   import App from './App.jsx'
   import './index.css'

   ReactDOM.createRoot(document.getElementById('root')).render(
     <React.StrictMode>
       <BrowserRouter>
         <App />
       </BrowserRouter>
     </React.StrictMode>,
   )
   ```

   **Create `admin-dashboard/src/App.jsx`:**
   ```jsx
   import { Routes, Route, Navigate } from 'react-router-dom'
   import { useState, useEffect } from 'react'
   import LoginScreen from './screens/LoginScreen'
   import DashboardScreen from './screens/DashboardScreen'
   import OrdersScreen from './screens/OrdersScreen'

   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

   function App() {
     const [isAuthenticated, setIsAuthenticated] = useState(false)
     const [user, setUser] = useState(null)
     const [loading, setLoading] = useState(true)

     useEffect(() => {
       const token = localStorage.getItem('admin_token')
       if (token) {
         // Verify token with backend
         fetch(`${API_BASE_URL}/admin/dashboard`, {
           headers: { Authorization: `Bearer ${token}` }
         })
         .then(res => res.ok ? setIsAuthenticated(true) : localStorage.removeItem('admin_token'))
         .catch(() => localStorage.removeItem('admin_token'))
         .finally(() => setLoading(false))
       } else {
         setLoading(false)
       }
     }, [])

     if (loading) {
       return <div className="flex items-center justify-center min-h-screen">Loading...</div>
     }

     return (
       <div className="min-h-screen bg-gray-100">
         <Routes>
           <Route 
             path="/login" 
             element={
               isAuthenticated ? 
               <Navigate to="/dashboard" replace /> : 
               <LoginScreen setAuth={setIsAuthenticated} setUser={setUser} />
             } 
           />
           <Route 
             path="/dashboard" 
             element={
               isAuthenticated ? 
               <DashboardScreen user={user} /> : 
               <Navigate to="/login" replace />
             } 
           />
           <Route 
             path="/orders" 
             element={
               isAuthenticated ? 
               <OrdersScreen /> : 
               <Navigate to="/login" replace />
             } 
           />
           <Route path="/" element={<Navigate to="/dashboard" replace />} />
         </Routes>
       </div>
     )
   }

   export default App
   ```

   **Create `admin-dashboard/vercel.json`:**
   ```json
   {
     "name": "pimpmycase-admin",
     "version": 2,
     "builds": [
       {
         "src": "package.json",
         "use": "@vercel/static-build",
         "config": {
           "distDir": "dist"
         }
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "/index.html"
       }
     ]
   }
   ```

2. **Deploy Admin Dashboard:**
   ```bash
   cd admin-dashboard
   vercel --prod
   ```

---

## 🔌 Step 4: Stripe Configuration

### 4.1 Stripe Dashboard Setup

1. **Login to Stripe Dashboard:** https://dashboard.stripe.com

2. **Get API Keys:**
   - Go to Developers → API Keys
   - Copy:
     - **Publishable key:** `pk_live_...` (for frontend)
     - **Secret key:** `sk_live_...` (for backend)

3. **Configure Webhooks:**
   - Go to Developers → Webhooks
   - Click "Add endpoint"
   - **Endpoint URL:** `https://pimpmycase-api.onrender.com/stripe-webhook`
   - **Events to send:**
     - `checkout.session.completed`
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
   - Copy the **Webhook secret:** `whsec_...`

4. **Test Payments:**
   - Use test card numbers:
     - Success: `4242 4242 4242 4242`
     - Decline: `4000 0000 0000 0002`

### 4.2 Frontend Stripe Integration

**Update your payment service:**
```javascript
// src/services/stripeService.js
import { loadStripe } from '@stripe/stripe-js'

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY)

export const createCheckoutSession = async (orderData) => {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/create-checkout-session`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(orderData),
  })

  if (!response.ok) {
    throw new Error('Failed to create checkout session')
  }

  const { checkout_url } = await response.json()
  window.location.href = checkout_url
}
```

---

## 📊 Step 5: Monitoring & Maintenance

### 5.1 Set Up Monitoring

**Create monitoring script `monitor.py`:**
```python
import requests
import time
import os
from datetime import datetime

def check_service_health():
    services = {
        "API": os.getenv("API_URL", "https://pimpmycase-api.onrender.com"),
        "Frontend": os.getenv("FRONTEND_URL", "https://your-frontend.vercel.app"),
        "Admin": os.getenv("ADMIN_URL", "https://your-admin.vercel.app")
    }
    
    for name, url in services.items():
        try:
            response = requests.get(f"{url}/health" if name == "API" else url, timeout=10)
            status = "✅ UP" if response.status_code == 200 else f"⚠️ DOWN ({response.status_code})"
            print(f"{datetime.now()} - {name}: {status}")
        except Exception as e:
            print(f"{datetime.now()} - {name}: ❌ ERROR - {e}")

if __name__ == "__main__":
    while True:
        check_service_health()
        time.sleep(300)  # Check every 5 minutes
```

### 5.2 Backup Strategy

**Database Backup (Run weekly):**
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.sql"

# Backup database
pg_dump "$DATABASE_URL" > "$BACKUP_FILE"

# Upload to cloud storage (optional)
# aws s3 cp "$BACKUP_FILE" s3://your-backup-bucket/
```

### 5.3 Performance Optimization

**Render Backend Optimization:**
```python
# Add to api_server.py
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Add compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["pimpmycase-api.onrender.com", "*.vercel.app"]
)

# Add request timeout
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=30.0)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"detail": "Request timeout"}
        )
```

---

## 🔧 Step 6: Domain & SSL Setup

### 6.1 Custom Domains (Optional)

**For Vercel:**
1. Go to Project Settings → Domains
2. Add your custom domain: `pimpmycase.com`
3. Configure DNS records as instructed

**For Render:**
1. Go to Service Settings → Custom Domains
2. Add: `api.pimpmycase.com`
3. Configure DNS CNAME record

### 6.2 Environment-Specific URLs

**Update your configuration:**
```javascript
// Frontend config
const config = {
  development: {
    API_BASE_URL: 'http://localhost:8000',
    STRIPE_PUBLISHABLE_KEY: 'pk_test_...'
  },
  production: {
    API_BASE_URL: 'https://api.pimpmycase.com',
    STRIPE_PUBLISHABLE_KEY: 'pk_live_...'
  }
}

export default config[import.meta.env.NODE_ENV || 'production']
```

---

## ✅ Deployment Checklist

### Pre-Deployment:
- [ ] Database schema created and tested
- [ ] All environment variables configured
- [ ] Stripe webhooks configured
- [ ] CORS settings updated with production URLs
- [ ] Error tracking (Sentry) configured
- [ ] Test all payment flows

### Post-Deployment:
- [ ] Verify all services are running
- [ ] Test complete user flow (QR → Payment → Confirmation)
- [ ] Test admin dashboard access
- [ ] Verify Stripe payments work
- [ ] Check database connections
- [ ] Set up monitoring alerts
- [ ] Create backup procedures

### Security Checklist:
- [ ] Change default admin password
- [ ] Use strong JWT secret keys
- [ ] Enable HTTPS everywhere
- [ ] Configure proper CORS origins
- [ ] Set up rate limiting
- [ ] Enable logging for security events

---

## 🆘 Troubleshooting

### Common Issues:

**1. Database Connection Errors:**
```bash
# Check connection string format
# Should be: postgresql://user:pass@host:port/db
# Not: postgres://user:pass@host:port/db
```

**2. CORS Errors:**
```python
# Add your exact Vercel URLs to CORS origins
allow_origins=[
    "https://your-app-name.vercel.app",
    "https://your-app-name-git-main-username.vercel.app",
    "https://your-custom-domain.com"
]
```

**3. Stripe Webhook Failures:**
```python
# Verify webhook secret in environment variables
# Check webhook URL is accessible
# Ensure proper error handling in webhook endpoint
```

**4. Build Failures:**
```bash
# Clear cache and rebuild
vercel --force
render rebuild-service
```

### Monitoring Commands:
```bash
# Check Render logs
render logs --service-id your-service-id

# Check Vercel logs
vercel logs

# Check database connection
psql "$DATABASE_URL" -c "SELECT version();"
```

---

## 💰 Cost Estimation

### Monthly Costs:
- **Render PostgreSQL:** $7/month (Starter) or Free (limited)
- **Render Web Service:** $7/month (Starter) or Free (limited)
- **Vercel:** Free (up to 100GB bandwidth)
- **Stripe:** 2.9% + 30p per transaction
- **Total Base Cost:** ~$14/month + transaction fees

### Scaling Considerations:
- Free tiers are suitable for development and low-traffic production
- Upgrade to paid plans as traffic increases
- Monitor usage and costs regularly

This comprehensive setup gives you a production-ready, scalable architecture using only Vercel and Render with integrated payments, admin dashboard, and monitoring capabilities.