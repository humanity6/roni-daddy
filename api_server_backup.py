"""PimpMyCase API - Modular FastAPI Server"""

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

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

# Include API routes
app.include_router(router)

# Include modular route modules
app.include_router(basic_router)
app.include_router(image_router)
app.include_router(payment_router)
app.include_router(vending_router)
app.include_router(chinese_router)

# Add CORS middleware
app.add_middleware(CORSMiddleware, **CORS_CONFIG)

# Add exception handlers
app.exception_handler(RequestValidationError)(validation_exception_handler)

# Basic endpoints (root, favicon, health, database management) are now handled by basic_router
# Image endpoints (generate, serve, styles) are now handled by image_router

# Image endpoints (generate, image serving, styles) are now handled by image_router

# Chinese API endpoints are now handled by chinese_router

# Order status update and print command endpoints moved to chinese_router

# payStatus endpoint is now handled by chinese_router

# Chinese payment status endpoint moved to chinese_router

# All remaining Chinese API endpoints moved to chinese_router
# All remaining vending machine endpoints moved to vending_router

# Final cleanup - removing all remaining endpoint functions (moved to modular routers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    """Get equipment information and status for Chinese partners"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Look up vending machine by equipment_id
        machine = db.query(VendingMachine).filter(VendingMachine.id == equipment_id).first()
        
        if not machine:
            return {
                "success": False,
                "error": "Equipment not found",
                "equipment_id": equipment_id
            }
        
        # Get recent orders for this machine
        recent_orders = db.query(Order).filter(Order.machine_id == equipment_id).order_by(desc(Order.created_at)).limit(10).all()
        
        return {
            "success": True,
            "equipment_id": equipment_id,
            "equipment_info": {
                "id": machine.id,
                "name": machine.name,
                "location": machine.location,
                "is_active": machine.is_active,
                "last_heartbeat": machine.last_heartbeat.isoformat() if machine.last_heartbeat else None,
                "created_at": machine.created_at.isoformat(),
                "status": "online" if machine.is_active else "offline"
            },
            "recent_orders": [
                {
                    "id": order.id,
                    "status": order.status,
                    "payment_status": order.payment_status,
                    "total_amount": float(order.total_amount),
                    "created_at": order.created_at.isoformat()
                }
                for order in recent_orders
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "equipment_id": equipment_id
        }

@app.post("/api/chinese/equipment/{equipment_id}/stock")
async def update_equipment_stock(
    equipment_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Update stock quantities for specific equipment"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Get request body
        body = await http_request.json()
        
        updated_models = []
        
        # Update stock for each model in the request
        for model_update in body.get('stock_updates', []):
            model_id = model_update.get('model_id')
            new_stock = model_update.get('stock', 0)
            
            if not model_id:
                continue
                
            # Find model by chinese_model_id or regular id
            model = db.query(PhoneModel).filter(
                (PhoneModel.chinese_model_id == model_id) | (PhoneModel.id == model_id)
            ).first()
            
            if model:
                old_stock = model.stock
                model.stock = max(0, new_stock)  # Ensure stock is not negative
                model.updated_at = datetime.now(timezone.utc)
                
                updated_models.append({
                    "model_id": model.id,
                    "chinese_model_id": model.chinese_model_id,
                    "name": model.name,
                    "old_stock": old_stock,
                    "new_stock": model.stock
                })
        
        db.commit()
        
        return {
            "success": True,
            "equipment_id": equipment_id,
            "updated_models": updated_models,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "equipment_id": equipment_id
        }

@app.get("/api/chinese/models/stock-status")
async def get_stock_status(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get real-time stock status for all phone models"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Get all phone models with their stock levels
        models = db.query(PhoneModel).options(joinedload(PhoneModel.brand)).filter(PhoneModel.is_available == True).all()
        
        stock_data = []
        for model in models:
            stock_data.append({
                "model_id": model.id,
                "chinese_model_id": model.chinese_model_id,
                "name": model.name,
                "brand": model.brand.name if model.brand else "Unknown",
                "stock": model.stock,
                "price": float(model.price),
                "is_available": model.is_available and model.stock > 0,
                "updated_at": model.updated_at.isoformat() if model.updated_at else model.created_at.isoformat()
            })
        
        return {
            "success": True,
            "models": stock_data,
            "total_models": len(stock_data),
            "in_stock_models": len([m for m in stock_data if m["stock"] > 0]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/chinese/print/trigger")
async def trigger_print_job(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Trigger printing after payment completion"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Get request body
        body = await http_request.json()
        order_id = body.get('order_id')
        
        if not order_id:
            return {
                "success": False,
                "error": "Order ID is required"
            }
        
        # Find the order
        order = db.query(Order).options(
            joinedload(Order.images),
            joinedload(Order.brand),
            joinedload(Order.phone_model)
        ).filter(Order.id == order_id).first()
        
        if not order:
            return {
                "success": False,
                "error": "Order not found",
                "order_id": order_id
            }
        
        # Check if order is paid
        if order.payment_status != "paid":
            return {
                "success": False,
                "error": "Order not paid yet",
                "order_id": order_id,
                "payment_status": order.payment_status
            }
        
        # Generate image URLs for printing
        image_urls = []
        if order.images:
            for img in order.images:
                if img.image_path:
                    # Generate full URL for Chinese API
                    filename = img.image_path.split('/')[-1]
                    image_url = f"https://pimpmycase.onrender.com/image/{filename}"
                    image_urls.append(image_url)
                    
                    # Update chinese_image_url for tracking
                    img.chinese_image_url = image_url
        
        # Update order status to indicate print job triggered
        order.status = "print_job_triggered" 
        order.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        
        return {
            "success": True,
            "order_id": order_id,
            "print_job_id": f"PRINT_{order_id}_{int(datetime.now(timezone.utc).timestamp())}",
            "image_urls": image_urls,
            "phone_model": f"{order.brand.name if order.brand else 'Unknown'} {order.phone_model.name if order.phone_model else 'Model'}",
            "status": "triggered",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/chinese/print/{order_id}/status")
async def get_print_status(
    order_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Check printing progress for an order"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Find the order
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {
                "success": False,
                "error": "Order not found",
                "order_id": order_id
            }
        
        return {
            "success": True,
            "order_id": order_id,
            "status": order.status,
            "payment_status": order.payment_status,
            "queue_number": order.queue_number,
            "estimated_completion": order.estimated_completion.isoformat() if order.estimated_completion else None,
            "notes": order.notes,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "order_id": order_id
        }

@app.get("/api/chinese/order/{order_id}/download-links")
async def get_order_download_links(
    order_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get UK-hosted download links for order images"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Find the order with images
        order = db.query(Order).options(joinedload(Order.images)).filter(Order.id == order_id).first()
        
        if not order:
            return {
                "success": False,
                "error": "Order not found",
                "order_id": order_id
            }
        
        download_links = []
        
        for img in order.images:
            if img.image_path:
                filename = img.image_path.split('/')[-1]
                download_url = generate_uk_download_url(filename)
                secure_token = generate_secure_download_token(filename, expiry_hours=48)  # 48 hour expiry for Chinese partners
                
                # Update chinese_image_url in database
                img.chinese_image_url = download_url
                
                download_links.append({
                    "image_id": img.id,
                    "image_type": img.image_type,
                    "download_url": download_url,
                    "secure_download_url": f"{download_url}?token={secure_token}",
                    "filename": filename,
                    "expiry_hours": 48,
                    "created_at": img.created_at.isoformat()
                })
        
        db.commit()
        
        return {
            "success": True,
            "order_id": order_id,
            "download_links": download_links,
            "total_images": len(download_links),
            "uk_hosting": True,
            "base_url": "https://pimpmycase.onrender.com",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "order_id": order_id
        }

@app.get("/api/chinese/images/batch-download")
async def get_batch_download_links(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get batch download links for multiple orders"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Get request parameters
        query_params = dict(http_request.query_params)
        order_ids = query_params.get('order_ids', '').split(',')
        order_ids = [oid.strip() for oid in order_ids if oid.strip()]
        
        if not order_ids:
            return {
                "success": False,
                "error": "No order IDs provided. Use ?order_ids=id1,id2,id3"
            }
        
        batch_downloads = []
        
        for order_id in order_ids:
            order = db.query(Order).options(joinedload(Order.images)).filter(Order.id == order_id).first()
            
            if not order:
                batch_downloads.append({
                    "order_id": order_id,
                    "success": False,
                    "error": "Order not found"
                })
                continue
            
            order_links = []
            for img in order.images:
                if img.image_path:
                    filename = img.image_path.split('/')[-1]
                    download_url = generate_uk_download_url(filename)
                    secure_token = generate_secure_download_token(filename, expiry_hours=48)
                    
                    # Update chinese_image_url in database
                    img.chinese_image_url = download_url
                    
                    order_links.append({
                        "image_id": img.id,
                        "download_url": download_url,
                        "secure_download_url": f"{download_url}?token={secure_token}",
                        "filename": filename
                    })
            
            batch_downloads.append({
                "order_id": order_id,
                "success": True,
                "images": order_links,
                "image_count": len(order_links)
            })
        
        db.commit()
        
        return {
            "success": True,
            "batch_downloads": batch_downloads,
            "total_orders": len(order_ids),
            "successful_orders": len([bd for bd in batch_downloads if bd["success"]]),
            "uk_hosting": True,
            "base_url": "https://pimpmycase.onrender.com",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Vending Machine Session Management APIs
# Vending machine create-session endpoint moved to vending_router

@app.get("/api/vending/session/{session_id}/status")
async def get_session_status(
    session_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get current status of a vending machine session"""
    try:
        # Security validation
        security_info = validate_session_security(http_request, session_id)
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            # Record failed attempt for potential brute force detection
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Reset failed attempts on successful session lookup
        security_manager.reset_failed_attempts(security_info["client_ip"])
        
        # Check if session has expired
        # Handle timezone-aware datetime comparison consistently
        current_time = datetime.now(timezone.utc)
        expires_at = session.expires_at
        
        # Ensure both datetimes have the same timezone info for comparison
        if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is not None:
            # expires_at is timezone-aware, keep current_time timezone-aware
            pass
        else:
            # expires_at is naive, make current_time naive too
            current_time = current_time.replace(tzinfo=None)
            
        if current_time > expires_at:
            session.status = "expired"
            # Decrement machine session count when expired
            security_manager.decrement_machine_sessions(session.machine_id)
            db.commit()
        
        # Update last activity for active sessions
        if session.status in ["active", "designing", "payment_pending"]:
            session.last_activity = datetime.now(timezone.utc)
            db.commit()
        
        # Helper function to safely format datetime
        def safe_datetime_format(dt):
            if dt is None:
                return None
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                return dt.replace(tzinfo=None).isoformat()
            return dt.isoformat()
        
        response_data = {
            "session_id": session.session_id,
            "status": session.status,
            "user_progress": session.user_progress,
            "expires_at": safe_datetime_format(session.expires_at),
            "created_at": safe_datetime_format(session.created_at),
            "last_activity": safe_datetime_format(session.last_activity),
            "machine_id": session.machine_id,
            "security_validated": True
        }
        
        if session.order_id:
            response_data["order_id"] = session.order_id
        if session.payment_amount:
            response_data["payment_amount"] = float(session.payment_amount)
        # Only return session_data to authorized requests
        if session.session_data and session.status != "expired":
            response_data["session_data"] = session.session_data
            
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")

@app.post("/api/vending/session/{session_id}/register-user")
async def register_user_with_session(
    session_id: str,
    request: QRParametersRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Register user with vending machine session when they scan QR code"""
    try:
        # Security validation
        security_info = validate_session_security(http_request, session_id)
        
        # Validate machine ID matches session
        if not security_manager.validate_machine_id(request.machine_id):
            raise HTTPException(status_code=400, detail="Invalid machine ID format")
        
        session = db.query(VendingMachineSession).options(joinedload(VendingMachineSession.vending_machine)).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has expired
        if datetime.now(timezone.utc) > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Validate machine ID matches session machine
        if session.machine_id != request.machine_id:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=400, detail="Machine ID mismatch")
        
        # Sanitize inputs
        user_agent = security_manager.sanitize_string_input(request.user_agent or "", 500)
        location = security_manager.sanitize_string_input(request.location or "", 200)
        
        # Update session with user info
        session.user_progress = "qr_scanned"
        session.last_activity = datetime.now(timezone.utc)
        session.user_agent = user_agent
        session.ip_address = security_info["client_ip"]  # Use validated IP from security check
        
        # Update session data with security tracking
        session_data = session.session_data or {}
        session_data.update({
            "qr_scanned_at": datetime.now(timezone.utc).isoformat(),
            "user_agent": user_agent,
            "ip_address": security_info["client_ip"],
            "location": location,
            "security_validated": True,
            "scan_security_info": security_info
        })
        session.session_data = session_data
        
        db.commit()
        db.refresh(session)
        
        return {
            "success": True,
            "session_id": session_id,
            "machine_info": {
                "id": session.machine_id,
                "name": session.vending_machine.name,
                "location": session.vending_machine.location
            },
            "expires_at": session.expires_at.isoformat(),
            "user_progress": session.user_progress,
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

@app.post("/api/vending/session/{session_id}/order-summary")
async def send_order_summary_to_vending_machine(
    session_id: str,
    request: OrderSummaryRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Send order summary to vending machine for payment processing"""
    try:
        # Security validation including payment amount
        security_info = validate_payment_security(http_request, request.payment_amount, session_id)
        
        # Validate order data size
        if not security_manager.validate_json_size(request.order_data, 100):
            raise HTTPException(status_code=400, detail="Order data too large")
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has expired
        if datetime.now(timezone.utc) > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Validate session state
        if session.status != "active" or session.user_progress not in ["qr_scanned", "designing", "design_complete"]:
            raise HTTPException(status_code=400, detail="Invalid session state for order summary")
        
        # Sanitize currency
        currency = security_manager.sanitize_string_input(request.currency, 10)
        if currency not in ["GBP", "USD", "EUR"]:
            currency = "GBP"  # Default to GBP
        
        # Update session with order details
        session.user_progress = "payment_pending"
        session.payment_amount = request.payment_amount
        session.last_activity = datetime.now(timezone.utc)
        
        # Store order summary in session data with security info
        session_data = session.session_data or {}
        session_data.update({
            "order_summary": request.order_data,
            "payment_amount": request.payment_amount,
            "currency": currency,
            "payment_requested_at": datetime.now(timezone.utc).isoformat(),
            "order_security_info": security_info
        })
        
        # IMPORTANT: SQLAlchemy doesn't detect changes to mutable JSON objects
        # We need to mark the attribute as changed to trigger persistence
        from sqlalchemy.orm.attributes import flag_modified
        session.session_data = session_data
        flag_modified(session, 'session_data')
        
        # Add debugging to verify data is stored
        print(f"DEBUG: Storing order summary for session {session_id}")
        print(f"DEBUG: Order data keys: {list(request.order_data.keys()) if request.order_data else 'None'}")
        print(f"DEBUG: Session data keys after update: {list(session_data.keys())}")
        print(f"DEBUG: Order summary stored: {'order_summary' in session_data}")
        
        try:
            # Use explicit transaction with proper isolation
            db.flush()  # Ensure changes are written to the transaction
            db.commit()
            
            # Verify data was actually committed
            db.refresh(session)
            if session.session_data and "order_summary" in session.session_data:
                print(f"DEBUG: Successfully verified order_summary in database for session {session_id}")
            else:
                print(f"ERROR: Order summary not found in database after commit for session {session_id}")
                print(f"ERROR: Session data keys in DB: {list(session.session_data.keys()) if session.session_data else 'None'}")
                raise HTTPException(status_code=500, detail="Failed to persist order data")
                
        except Exception as e:
            db.rollback()
            print(f"ERROR: Database transaction failed for session {session_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to store order summary: {str(e)}")
        
        return {
            "success": True,
            "message": "Order summary sent to vending machine",
            "session_id": session_id,
            "payment_amount": request.payment_amount,
            "currency": currency,
            "status": "payment_pending",
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send order summary: {str(e)}")

@app.post("/api/vending/session/{session_id}/confirm-payment")
async def confirm_vending_machine_payment(
    session_id: str,
    request: VendingPaymentConfirmRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Confirm payment received from vending machine"""
    try:
        # Security validation including payment amount
        security_info = validate_payment_security(http_request, request.payment_amount, session_id)
        
        # Validate payment data size
        if request.payment_data and not security_manager.validate_json_size(request.payment_data, 50):
            raise HTTPException(status_code=400, detail="Payment data too large")
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has expired
        if datetime.now(timezone.utc) > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Validate session state
        if session.user_progress != "payment_pending":
            raise HTTPException(status_code=400, detail="Session not ready for payment confirmation")
        
        # Validate payment amount matches order
        if session.payment_amount and abs(float(session.payment_amount) - request.payment_amount) > 0.01:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=400, detail="Payment amount does not match order total")
        
        # Sanitize transaction ID and payment method
        transaction_id = security_manager.sanitize_string_input(request.transaction_id, 100)
        payment_method = security_manager.sanitize_string_input(request.payment_method, 50)
        
        # Validate payment method
        valid_methods = ["card", "cash", "contactless", "mobile"]
        if payment_method not in valid_methods:
            raise HTTPException(status_code=400, detail="Invalid payment method")
        
        # Update session with payment confirmation
        session.status = "payment_completed"
        session.payment_method = "vending_machine"
        session.payment_confirmed_at = datetime.now(timezone.utc)
        session.last_activity = datetime.now(timezone.utc)
        
        # Store payment details with security info
        session_data = session.session_data or {}
        session_data.update({
            "payment_confirmed_at": datetime.now(timezone.utc).isoformat(),
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "payment_data": request.payment_data or {},
            "payment_security_info": security_info,
            "payment_amount_verified": request.payment_amount
        })
        session.session_data = session_data
        
        # Decrement machine session count as payment is complete
        security_manager.decrement_machine_sessions(session.machine_id)
        
        # Create order from session data after payment confirmation
        order_id = None
        try:
            if session_data.get("order_summary"):
                order_summary = session_data["order_summary"]
                
                # Extract order details from session data
                brand_name = order_summary.get("brand", "")
                model_name = order_summary.get("model", "")
                template_id = order_summary.get("template", {}).get("id", "")
                
                # Look up entities from database
                brand = BrandService.get_brand_by_name(db, brand_name) if brand_name else None
                if not brand:
                    raise HTTPException(status_code=400, detail=f"Brand '{brand_name}' not found")
                
                model = PhoneModelService.get_model_by_name(db, model_name, brand.id) if model_name else None
                if not model:
                    raise HTTPException(status_code=400, detail=f"Model '{model_name}' not found for brand '{brand_name}'")
                
                template = TemplateService.get_template_by_id(db, template_id) if template_id else None
                if not template:
                    raise HTTPException(status_code=400, detail=f"Template '{template_id}' not found")
                
                # Create order data
                order_data = {
                    "session_id": session_id,
                    "brand_id": brand.id,
                    "model_id": model.id,
                    "template_id": template.id,
                    "user_data": order_summary,
                    "total_amount": request.payment_amount,
                    "currency": session_data.get("currency", "GBP"),
                    "status": "paid",
                    "payment_status": "paid",
                    "payment_method": "vending_machine",
                    "paid_at": datetime.now(timezone.utc),
                    "vending_transaction_id": transaction_id,
                    "vending_session_id": session_id
                }
                
                # Create the order
                order = OrderService.create_order(db, order_data)
                order_id = order.id
                
                # Update session with order ID
                session.order_id = order_id
                session_data["order_id"] = order_id
                session.session_data = session_data
                
                db.commit()
                
                # Send print command to Chinese manufacturers
                try:
                    # Prepare image URLs from order data
                    image_urls = []
                    if order_summary.get("designImage"):
                        # Store design image and get URL
                        design_image = order_summary["designImage"]
                        if design_image.startswith("data:image"):
                            # Save base64 image and create URL
                            timestamp = int(time.time())
                            filename = f"vending_order_{order_id}_{timestamp}.png"
                            generated_dir = ensure_directories()
                            file_path = generated_dir / filename
                            
                            # Convert base64 to image file
                            import base64
                            _, base64_data = design_image.split(',', 1)
                            image_bytes = base64.b64decode(base64_data)
                            
                            with open(file_path, 'wb') as f:
                                f.write(image_bytes)
                            
                            # Create full URL for Chinese API
                            image_url = f"https://pimpmycase.onrender.com/image/{filename}"
                            image_urls.append(image_url)
                        else:
                            image_urls.append(design_image)
                    
                    if not image_urls:
                        print(f"⚠️ No images found for order {order_id}, skipping print command")
                    else:
                        # Create print command request
                        print_request = PrintCommandRequest(
                            order_id=order_id,
                            image_urls=image_urls,
                            phone_model=f"{brand_name} {model_name}",
                            customer_info={
                                "vending_machine_id": session.machine_id,
                                "session_id": session_id,
                                "transaction_id": transaction_id,
                                "payment_method": payment_method
                            },
                            priority=1
                        )
                        
                        # Send print command
                        await send_print_command(print_request, db)
                        print(f"✅ Print command sent for order {order_id}")
                        
                except Exception as print_error:
                    print(f"⚠️ Failed to send print command for order {order_id}: {print_error}")
                    # Don't fail the payment confirmation if print command fails
                    OrderService.update_order_status(db, order_id, "payment_completed_print_failed", {
                        "print_error": str(print_error),
                        "print_error_at": datetime.now(timezone.utc).isoformat()
                    })
                
            else:
                print(f"⚠️ No order summary found in session {session_id}, cannot create order")
                
        except Exception as order_error:
            print(f"⚠️ Failed to create order for session {session_id}: {order_error}")
            # Don't fail the payment confirmation if order creation fails
            db.rollback()
            db.commit()  # Commit the session updates without the order
        
        return {
            "success": True,
            "message": "Payment confirmed successfully and order created",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "order_id": order_id,
            "status": "payment_completed",
            "next_steps": "Order has been sent for printing" if order_id else "Payment confirmed, but order creation failed",
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm payment: {str(e)}")

# Security validation endpoint
@app.post("/api/vending/session/{session_id}/validate")
async def validate_session_security_endpoint(
    session_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Validate session security for external monitoring"""
    try:
        # Security validation
        security_info = validate_session_security(http_request, session_id)
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check session health
        is_expired = datetime.now(timezone.utc) > session.expires_at
        is_active = session.status in ["active", "designing", "payment_pending"]
        
        return {
            "session_id": session_id,
            "valid": True,
            "security_validated": True,
            "session_health": {
                "is_expired": is_expired,
                "is_active": is_active,
                "status": session.status,
                "user_progress": session.user_progress,
                "expires_at": session.expires_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            },
            "security_info": security_info,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session validation failed: {str(e)}")

@app.get("/api/vending/session/{session_id}/order-info")
async def get_vending_order_info(
    session_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get order information for vending machine payment processing"""
    try:
        # Security validation
        security_info = validate_session_security(http_request, session_id)
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Refresh session from database to ensure we have latest data
        db.refresh(session)
        
        # Check if session has expired
        if datetime.now(timezone.utc) > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Check if session has order information with detailed debugging
        print(f"DEBUG: Retrieving order info for session {session_id}")
        print(f"DEBUG: Session status: {session.status}, progress: {session.user_progress}")
        print(f"DEBUG: Session has session_data: {session.session_data is not None}")
        
        if not session.session_data:
            print(f"ERROR: Session {session_id} has no session_data")
            raise HTTPException(status_code=400, detail="No session data available for this session")
        
        print(f"DEBUG: Session {session_id} session_data keys: {list(session.session_data.keys())}")
        
        if not session.session_data.get("order_summary"):
            print(f"ERROR: Session {session_id} missing order_summary key")
            print(f"ERROR: Available keys: {list(session.session_data.keys())}")
            
            # Check if order data exists under a different key structure
            for key, value in session.session_data.items():
                if isinstance(value, dict) and any(k in str(value).lower() for k in ['brand', 'model', 'template']):
                    print(f"DEBUG: Found potential order data in key '{key}': {type(value)}")
            
            raise HTTPException(status_code=400, detail="No order information available for this session")
        
        order_summary = session.session_data["order_summary"]
        
        # Extract key order information for vending machine display
        order_info = {
            "session_id": session_id,
            "order_summary": {
                "brand": order_summary.get("brand", ""),
                "model": order_summary.get("model", ""),
                "template": order_summary.get("template", {}),
                "color": order_summary.get("color", ""),
                "inputText": order_summary.get("inputText", ""),
                "selectedFont": order_summary.get("selectedFont", ""),
                "selectedTextColor": order_summary.get("selectedTextColor", "")
            },
            "payment_amount": session.payment_amount,
            "currency": session.session_data.get("currency", "GBP"),
            "machine_info": {
                "id": session.machine_id,
                "location": session.qr_data.get("location") if session.qr_data else None
            },
            "session_status": {
                "status": session.status,
                "user_progress": session.user_progress,
                "expires_at": session.expires_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            },
            "security_validated": True
        }
        
        # Update last activity
        session.last_activity = datetime.now(timezone.utc)
        db.commit()
        
        return order_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get order info: {str(e)}")

@app.delete("/api/vending/session/{session_id}")
async def cleanup_vending_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Clean up expired or cancelled vending machine session"""
    try:
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update status to cancelled and keep record for audit
        session.status = "cancelled"
        session.last_activity = datetime.now(timezone.utc)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Session cancelled successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup session: {str(e)}")

# create-checkout-session endpoint moved to payment_router

# payment-success endpoint moved to payment_router

# All payment endpoints moved to payment_router

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 