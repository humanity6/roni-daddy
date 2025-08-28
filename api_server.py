"""PimpMyCase API - Modular FastAPI Server"""

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

# Standard library imports
from typing import Optional, List
import requests
import secrets
import traceback
import os
import time
import uuid
import json
import stripe
import logging

# Database imports
from database import get_db, create_tables
from db_services import OrderService, OrderImageService, BrandService, PhoneModelService, TemplateService
from models import PhoneModel, Template, VendingMachine, VendingMachineSession, Order, OrderImage

# API routes
from api_routes import router

# Backend route modules
from backend.routes.basic import router as basic_router
from backend.routes.image import router as image_router
from backend.routes.payment import router as payment_router
from backend.routes.vending import router as vending_router
from backend.routes.chinese_api import router as chinese_router
from backend.routes.admin import router as admin_router

# Security middleware
from security_middleware import (
    validate_session_security, 
    validate_machine_security, 
    validate_payment_security,
    validate_relaxed_api_security,
    security_manager
)

# AI prompts
from ai_prompts import STYLE_PROMPTS, generate_style_prompt

# Backend modules
from backend.config.settings import API_TITLE, API_VERSION, JWT_SECRET_KEY
from backend.config.cors import CORS_CONFIG
from backend.schemas.payment import CheckoutSessionRequest, PaymentSuccessRequest
from backend.schemas.chinese_api import (
    OrderStatusUpdateRequest, PrintCommandRequest, ChinesePayStatusRequest, ChinesePaymentDataRequest
)
from backend.schemas.vending import (
    CreateSessionRequest, SessionStatusResponse, OrderSummaryRequest,
    VendingPaymentConfirmRequest, QRParametersRequest
)
from backend.services.ai_service import get_openai_client, generate_image_gpt_image_1
from backend.services.image_service import convert_image_for_api, save_generated_image, ensure_directories
from backend.services.file_service import generate_uk_download_url, generate_secure_download_token
from backend.services.payment_service import initialize_stripe
from backend.utils.helpers import generate_third_id, get_mobile_model_id
from backend.middleware.exception_handlers import validation_exception_handler

# SQLAlchemy imports
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from datetime import datetime, timezone

# Initialize services
stripe_client = initialize_stripe()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pimpmycase_api.log', encoding='utf-8')
    ]
)

# Set specific loggers
logger = logging.getLogger(__name__)
logging.getLogger('backend.services.chinese_payment_service').setLevel(logging.DEBUG)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Database lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    try:
        create_tables()
        print("Database tables created/verified")
    except Exception as e:
        print(f"Database initialization error: {e}")
    yield

# Initialize FastAPI app
app = FastAPI(title=API_TITLE, version=API_VERSION, lifespan=lifespan)

# Add CORS middleware
app.add_middleware(CORSMiddleware, **CORS_CONFIG)

# Add exception handlers
app.exception_handler(RequestValidationError)(validation_exception_handler)

# Include API routes FIRST (higher priority)
app.include_router(router)

# Include modular route modules
app.include_router(basic_router)
app.include_router(image_router, prefix="/api/images")
app.include_router(payment_router)
app.include_router(vending_router)
app.include_router(chinese_router)
app.include_router(admin_router)

# Mount static files for frontend (after API routes)
import os
if os.path.exists("dist"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")
    app.mount("/fonts", StaticFiles(directory="dist/fonts"), name="fonts") 
    app.mount("/ui-mockups", StaticFiles(directory="dist/ui-mockups"), name="ui-mockups")
    
    # Serve individual static files and SPA fallback (LAST - lowest priority)
    @app.get("/{filename:path}")
    async def serve_static_files(filename: str):
        """Serve static files from dist directory or SPA fallback"""
        # List of files that should be served from dist
        static_files = [
            "index.html", "manifest.json", "sw.js", ".htaccess",
            "logo.png", "filmstrip-case.png", "filmstrip-template.png", 
            "blueblob.svg", "google blob.svg", "iphoneblob.svg", "samsung blob.svg",
            "phone cover cropped.png", "phone-template.png", "logo (original).png"
        ]
        
        # If it's a static file, serve it
        if filename in static_files or filename == "":
            file_path = os.path.join("dist", filename if filename else "index.html")
            if os.path.exists(file_path):
                return FileResponse(file_path)
        
        # For all other paths (SPA routes), serve index.html
        return FileResponse("dist/index.html")

# All endpoints have been moved to modular route modules:
# - Basic endpoints (root, favicon, health, database) -> basic_router
# - Image endpoints (generate, serve, styles) -> image_router  
# - Payment endpoints (checkout, success, webhook) -> payment_router
# - Vending machine endpoints (sessions, QR codes) -> vending_router
# - Chinese API endpoints (equipment, printing, downloads) -> chinese_router

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)