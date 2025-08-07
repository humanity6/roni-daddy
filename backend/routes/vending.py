"""Vending machine API routes"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from database import get_db
from backend.schemas.vending import (
    CreateSessionRequest, SessionStatusResponse, OrderSummaryRequest,
    VendingPaymentConfirmRequest, QRParametersRequest
)
from backend.schemas.chinese_api import PrintCommandRequest, ChinesePaymentDataRequest
from backend.utils.helpers import generate_third_id, get_mobile_model_id
from backend.services.image_service import ensure_directories
from security_middleware import (
    validate_session_security, validate_machine_security, 
    validate_payment_security, security_manager
)
from db_services import BrandService, PhoneModelService, TemplateService, OrderService
from models import VendingMachine, VendingMachineSession, Order
from datetime import datetime, timezone, timedelta
import secrets
import time
import base64

router = APIRouter(prefix="/api/vending")

@router.post("/create-session")
async def create_vending_session(
    request: CreateSessionRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Create a new vending machine session for QR code generation"""
    try:
        # Security validation
        security_info = validate_machine_security(http_request, request.machine_id)
        
        # Sanitize inputs
        machine_id = security_manager.sanitize_string_input(request.machine_id, 50)
        location = security_manager.sanitize_string_input(request.location or "", 200)
        
        # Validate timeout range
        timeout_minutes = max(5, min(60, request.session_timeout_minutes or 30))
        
        # Validate metadata size
        if request.metadata and not security_manager.validate_json_size(request.metadata, 10):
            raise HTTPException(status_code=400, detail="Metadata too large")
        
        # Validate vending machine exists and is active
        vending_machine = db.query(VendingMachine).filter(
            VendingMachine.id == machine_id,
            VendingMachine.is_active == True
        ).first()
        if not vending_machine:
            raise HTTPException(status_code=404, detail="Vending machine not found or inactive")
        
        # Check machine session limit
        if not security_manager.validate_machine_session_limit(machine_id):
            raise HTTPException(status_code=429, detail="Machine session limit exceeded")
        
        # Generate unique session ID with enhanced randomness
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        random_suffix = secrets.token_hex(4).upper()
        session_id = f"{machine_id}_{timestamp}_{random_suffix}"
        
        # Calculate expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=timeout_minutes)
        
        # Create session record with security info
        session = VendingMachineSession(
            session_id=session_id,
            machine_id=machine_id,
            status="active",
            user_progress="started",
            expires_at=expires_at,
            ip_address=security_info["client_ip"],
            created_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            qr_data={
                "machine_id": machine_id,
                "location": location,
                "timeout_minutes": timeout_minutes,
                "metadata": request.metadata or {},
                "security_info": security_info
            }
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Increment machine session count
        security_manager.increment_machine_sessions(machine_id)
        
        # Generate QR URL with URL encoding for location
        from urllib.parse import quote
        qr_url = f"https://pimpmycase.shop/?qr=true&machine_id={machine_id}&session_id={session_id}"
        if location:
            qr_url += f"&location={quote(location)}"
        
        return {
            "success": True,
            "session_id": session_id,
            "qr_url": qr_url,
            "expires_at": expires_at.isoformat(),
            "timeout_minutes": timeout_minutes,
            "machine_info": {
                "id": vending_machine.id,
                "name": vending_machine.name,
                "location": vending_machine.location
            },
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.post("/session/{session_id}/init-payment")
async def initialize_vending_payment(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Initialize payment with Chinese manufacturers for vending machine session"""
    try:
        # Get vending session
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has expired
        if datetime.now(timezone.utc) > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Get session data
        if not session.session_data or not session.session_data.get("order_summary"):
            raise HTTPException(status_code=400, detail="No order data found in session")
        
        order_summary = session.session_data["order_summary"]
        
        # Extract order details
        brand_name = order_summary.get("brand", "")
        model_name = order_summary.get("model", "")
        payment_amount = session.payment_amount or order_summary.get("price", 19.99)
        
        # Look up phone model in database
        brand = BrandService.get_brand_by_name(db, brand_name) if brand_name else None
        phone_model = PhoneModelService.get_model_by_name(db, model_name, brand.id) if brand and model_name else None
        
        # Generate third_id
        third_id = generate_third_id()
        
        # Get mobile model ID for Chinese API
        mobile_model_id = get_mobile_model_id(phone_model, db)
        
        # Prepare Chinese payment data
        from backend.schemas.chinese_api import ChinesePaymentDataRequest
        chinese_payment_data = ChinesePaymentDataRequest(
            mobile_model_id=mobile_model_id,
            device_id=session.machine_id,  # Use actual machine ID as device ID
            third_id=third_id,
            pay_amount=float(payment_amount),
            pay_type=6  # Card payment for vending machines
        )
        
        # Store third_id in session for tracking
        session_data = session.session_data or {}
        session_data["chinese_third_id"] = third_id
        session_data["payment_initiated_at"] = datetime.now(timezone.utc).isoformat()
        session.session_data = session_data
        db.commit()
        
        return {
            "success": True,
            "message": "Payment initialized with Chinese manufacturers",
            "session_id": session_id,
            "third_id": third_id,
            "payment_amount": payment_amount,
            "mobile_model_id": mobile_model_id,
            "device_id": session.machine_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Payment initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to initialize payment: {str(e)}")

@router.get("/session/{session_id}/status")
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
        current_time = datetime.now(timezone.utc)
        expires_at = session.expires_at
        
        # Ensure both datetimes have the same timezone info for comparison
        if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is not None:
            pass
        else:
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

@router.post("/session/{session_id}/register-user")
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
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has expired
        if datetime.now(timezone.utc) > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Update session with user registration
        session.user_progress = "registered"
        session.last_activity = datetime.now(timezone.utc)
        
        # Store registration data
        if not session.session_data:
            session.session_data = {}
        
        session.session_data["user_registered_at"] = datetime.now(timezone.utc).isoformat()
        session.session_data["registration_ip"] = security_info["client_ip"]
        
        db.commit()
        
        return {
            "success": True,
            "session_id": session_id,
            "status": session.status,
            "user_progress": session.user_progress,
            "machine_id": session.machine_id,
            "message": "User successfully registered with session"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

@router.delete("/session/{session_id}")
async def cleanup_vending_session(
    session_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Clean up and delete vending machine session"""
    try:
        # Security validation
        security_info = validate_session_security(http_request, session_id)
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Decrement machine session count
        security_manager.decrement_machine_sessions(session.machine_id)
        
        # Delete the session
        db.delete(session)
        db.commit()
        
        return {
            "success": True,
            "message": "Session cleaned up successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup session: {str(e)}")