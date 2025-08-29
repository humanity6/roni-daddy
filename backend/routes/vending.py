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
import json
import time
import base64
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter(prefix="/api/vending")

@router.post("/create-session")
async def create_vending_session(
    request: CreateSessionRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Create a new vending machine session for QR code generation"""
    try:
        print(f"=== CREATE VENDING SESSION START ===")
        print(f"Request: {request.dict()}")
        print(f"Machine ID: {request.machine_id}")
        print(f"Location: {request.location}")
        
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
        
        # Validate vending machine exists and is active, or auto-create for Chinese integrations
        vending_machine = db.query(VendingMachine).filter(
            VendingMachine.id == machine_id,
            VendingMachine.is_active == True
        ).first()
        
        if not vending_machine:
            # Auto-create vending machine for Chinese API integrations
            print(f"Auto-creating vending machine for device_id: {machine_id}")
            
            vending_machine = VendingMachine(
                id=machine_id,
                name=f"Chinese Vending Machine {machine_id}",
                location=location or "Chinese Integration - Location TBD",
                is_active=True,
                qr_config={
                    "auto_created": True,
                    "created_for": "chinese_integration",
                    "timeout_minutes": timeout_minutes
                },
                created_at=datetime.now(timezone.utc)
            )
            
            try:
                db.add(vending_machine)
                db.flush()  # Flush to get the ID assigned
                print(f"Successfully auto-created vending machine: {machine_id}")
            except Exception as e:
                print(f"Failed to auto-create vending machine: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to create vending machine: {str(e)}")
        
        # Check machine session limit with automatic cleanup
        if not security_manager.validate_machine_session_limit(machine_id, db_session=db):
            retry_info = security_manager.get_retry_delay(machine_id, attempt_count=1)
            raise HTTPException(
                status_code=429, 
                detail=f"Machine session limit exceeded. {retry_info['message']}",
                headers={"Retry-After": str(int(retry_info['retry_after_seconds']))}
            )
        
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
        
        print(f"Successfully created vending session:")
        print(f"- Session ID: {session_id}")
        print(f"- Machine: {vending_machine.name} ({vending_machine.id})")
        print(f"- QR URL: {qr_url}")
        print(f"=== CREATE VENDING SESSION END ===")
        
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

@router.get("/session/{session_id}/health")
async def check_session_health(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Check if a vending session is still valid and active"""
    try:
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            return {
                "valid": False,
                "status": "not_found",
                "message": "Session not found. Please rescan the QR code to start a new session."
            }
        
        # Check if session has expired
        now = datetime.now(timezone.utc)
        if now > session.expires_at:
            # Update session status if needed
            if session.status == "active":
                session.status = "expired"
                db.commit()
                security_manager.decrement_machine_sessions(session.machine_id)
            
            return {
                "valid": False,
                "status": "expired", 
                "message": "Session has expired. Please rescan the QR code to start a new session.",
                "expired_at": session.expires_at.isoformat()
            }
        
        # Check session status
        if session.status != "active":
            return {
                "valid": False,
                "status": session.status,
                "message": f"Session is {session.status}. Please rescan the QR code to start a new session."
            }
        
        # Calculate time remaining
        time_remaining = (session.expires_at - now).total_seconds()
        
        return {
            "valid": True,
            "status": "active",
            "message": "Session is active",
            "expires_at": session.expires_at.isoformat(),
            "time_remaining_seconds": int(time_remaining),
            "machine_id": session.machine_id,
            "user_progress": session.user_progress
        }
        
    except Exception as e:
        return {
            "valid": False,
            "status": "error",
            "message": "Unable to check session health. Please rescan the QR code to start a new session."
        }

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
        brand_id = order_summary.get("brand_id", "")
        payment_amount = session.payment_amount or order_summary.get("price", 19.99)
        
        # DEBUG: Log the extracted values to identify the issue
        print(f"🔍 DEBUG - Extracted order details:")
        print(f"  - brand_name: '{brand_name}'")
        print(f"  - brand_id: '{brand_id}'") 
        print(f"  - model_name: '{model_name}'")
        print(f"  - Available order_summary keys: {list(order_summary.keys())}")
        
        # Validate stock availability with Chinese API
        mobile_model_id = None
        stock_available = False
        
        # CRITICAL FIX: Ensure we have a valid brand_id for Chinese API calls
        if not brand_id and brand_name:
            # Fallback: try to get Chinese brand_id from our database
            try:
                from db_services import BrandService
                brand_obj = BrandService.get_brand_by_name(db, brand_name)
                if brand_obj and hasattr(brand_obj, 'chinese_brand_id'):
                    brand_id = brand_obj.chinese_brand_id
                    print(f"✅ Found Chinese brand_id from database: {brand_id}")
                else:
                    print(f"❌ No Chinese brand_id found for brand: {brand_name}")
            except Exception as e:
                print(f"❌ Error looking up Chinese brand_id: {str(e)}")
        
        if brand_id and session.machine_id:
            try:
                # Import Chinese API service
                from backend.services.chinese_payment_service import get_chinese_stock
                
                # DEBUG: Log the parameters being passed to Chinese API
                print(f"🚀 Calling get_chinese_stock with:")
                print(f"  - device_id (machine_id): '{session.machine_id}'")
                print(f"  - brand_id: '{brand_id}'")
                
                # Get real-time stock data from Chinese API
                stock_result = get_chinese_stock(session.machine_id, brand_id)
                print(f"📦 Stock validation result: {stock_result.get('success')}, items: {len(stock_result.get('stock_items', []))}")
                
                if stock_result.get("success"):
                    stock_items = stock_result.get("stock_items", [])
                    
                    # Find the specific model in stock and get mobile_shell_id
                    mobile_shell_id = None
                    for item in stock_items:
                        if (item.get("mobile_model_name") == model_name and 
                            item.get("stock", 0) > 0):
                            mobile_model_id = item.get("mobile_model_id")
                            mobile_shell_id = item.get("mobile_shell_id")
                            stock_available = True
                            print(f"✅ Stock validated: {model_name} (ID: {mobile_model_id}, Shell: {mobile_shell_id}) has {item.get('stock')} units")
                            break
                    
                    if not stock_available:
                        print(f"❌ Stock validation failed: {model_name} not available or out of stock")
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Selected model '{model_name}' is not available or out of stock"
                        )
                else:
                    print(f"⚠️  Chinese API stock check failed: {stock_result.get('message')}")
                    # Fallback to local database lookup
                    brand = BrandService.get_brand_by_name(db, brand_name) if brand_name else None
                    phone_model = PhoneModelService.get_model_by_name(db, model_name, brand.id) if brand and model_name else None
                    mobile_model_id = get_mobile_model_id(phone_model, db)
                    
            except Exception as e:
                print(f"❌ Stock validation error: {str(e)}")
                # Fallback to local database lookup
                brand = BrandService.get_brand_by_name(db, brand_name) if brand_name else None
                phone_model = PhoneModelService.get_model_by_name(db, model_name, brand.id) if brand and model_name else None
                mobile_model_id = get_mobile_model_id(phone_model, db)
        else:
            print(f"❌ Missing required data for stock validation: brand_id={brand_id}, machine_id={session.machine_id}")
            raise HTTPException(status_code=400, detail="Missing brand ID or machine ID for stock validation")
        
        # Generate third_id
        third_id = generate_third_id()
        
        # Ensure we have a mobile_model_id
        if not mobile_model_id:
            raise HTTPException(status_code=400, detail="Could not determine mobile model ID for payment processing")
        
        # Prepare Chinese payment data
        from backend.schemas.chinese_api import ChinesePaymentDataRequest
        chinese_payment_data = ChinesePaymentDataRequest(
            mobile_model_id=mobile_model_id,
            device_id=session.machine_id,  # Use actual machine ID as device ID
            third_id=third_id,
            pay_amount=float(payment_amount),
            pay_type=5  # Vending machine payment (corrected from 6 to 5)
        )
        
        # Call Chinese API endpoint
        try:
            from backend.routes.chinese_api import send_payment_data_to_chinese_api
            # Create mock request object with headers attribute
            class MockRequest:
                def __init__(self):
                    self.client = type('obj', (object,), {'host': '127.0.0.1'})
                    self.headers = {}  # Fix: Add missing headers attribute
                    
            mock_request = MockRequest()
            chinese_response = await send_payment_data_to_chinese_api(
                chinese_payment_data, 
                mock_request, 
                db
            )
        except Exception as e:
            print(f"❌ Chinese payData API call failed: {e}")
            raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")
        
        # Check if payData was successful before proceeding
        if not chinese_response or chinese_response.get("code") != 200:
            print(f"❌ Chinese payData API returned error: {chinese_response}")
            raise HTTPException(status_code=500, detail=f"Payment initialization failed: {chinese_response.get('msg', 'Unknown error')}")
        
        print(f"✅ PayData successful, now calling orderData immediately...")
        
        # CRITICAL: Call orderData immediately after successful payData (no webhook dependency)
        try:
            from backend.services.chinese_payment_service import send_order_data_to_chinese_api
            import time
            
            # Generate order third_id in OREN format (different from payment third_id)
            current_date = datetime.now().strftime("%y%m%d")  # yyMMdd format
            order_sequence = int(time.time() * 1000) % 1000000  # 6 digits
            order_third_id = f"OREN{current_date}{order_sequence:06d}"
            
            # Get final image URL from session data 
            order_summary = session.session_data.get('order_summary', {})
            final_image_url = session.session_data.get('final_image_url')
            if not final_image_url and order_summary:
                final_image_url = order_summary.get('finalImagePublicUrl')
                
            if not final_image_url:
                print(f"❌ No final image URL found in session data")
                raise HTTPException(status_code=400, detail="Final image URL missing for order creation")
            
            # Generate partner token for Chinese API image access  
            if final_image_url and 'pimpmycase.onrender.com' in final_image_url:
                try:
                    from backend.services.file_service import get_file_service
                    file_service = get_file_service()
                    
                    # Extract filename from URL
                    if '/image/' in final_image_url:
                        base_url = final_image_url.split('?')[0]
                        filename = base_url.split('/image/')[-1]
                        
                        # Generate partner token for Chinese API (24h expiry)
                        token_info = file_service.generate_partner_token(filename, "chinese_api", 24 * 3600)
                        if token_info.get('success'):
                            final_image_url = f"{base_url}?token={token_info['token']}"
                            print(f"✅ Generated Chinese API partner token for image: {filename}")
                        else:
                            print(f"❌ Failed to generate partner token for {filename}: {token_info.get('error')}")
                except Exception as e:
                    print(f"❌ Error generating partner token for Chinese API: {str(e)}")
            
            print(f"🚀 CALLING ORDERDATA ENDPOINT:")
            print(f"URL: http://app-dev.deligp.com:8500/mobileShell/en/order/orderData")
            print(f"Payment Third ID: {third_id}")
            print(f"Order Third ID: {order_third_id}")
            print(f"Mobile Model ID: {mobile_model_id}")
            print(f"Mobile Shell ID: {mobile_shell_id}")
            print(f"Device ID: {session.machine_id}")
            print(f"Image URL: {final_image_url}")
            
            # Call orderData immediately
            order_response = send_order_data_to_chinese_api(
                third_pay_id=third_id,  # Use payment third_id here
                third_id=order_third_id,  # Use order third_id here
                mobile_model_id=mobile_model_id,
                pic=final_image_url,
                device_id=session.machine_id,
                mobile_shell_id=mobile_shell_id
            )
            
            print(f"✅ ORDERDATA CALL COMPLETED!")
            print(f"Response: {json.dumps(order_response, indent=2, ensure_ascii=False) if order_response else 'None'}")
            
            # Update session with order information
            if order_response and order_response.get('code') == 200:
                session.user_progress = "order_submitted"
                session.status = "payment_completed"
                print(f"✅ Order successfully sent to Chinese API - Session {session_id} completed")
                
                # Store queue number and order info
                order_data = order_response.get('data', {})
                queue_number = order_data.get('queue_no')
                chinese_order_id = order_data.get('id')
                
                order_info = {
                    'chinese_order_response': order_response,
                    'order_third_id': order_third_id,
                    'payment_confirmed_at': datetime.now(timezone.utc).isoformat(),
                    'queue_number': queue_number,
                    'chinese_order_id': chinese_order_id
                }
                
            else:
                print(f"❌ OrderData call failed: {order_response}")
                raise HTTPException(status_code=500, detail=f"Order creation failed: {order_response.get('msg') if order_response else 'No response'}")
                
        except Exception as order_err:
            print(f"❌ Failed to create order after payment: {str(order_err)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Order creation failed: {str(order_err)}")
        
        # Store all session data including order information
        session_data = session.session_data or {}
        
        # Store payment data
        if "payment_data" not in session_data:
            session_data["payment_data"] = {}
        session_data["payment_data"]["third_id"] = third_id
        session_data["payment_data"]["amount"] = payment_amount
        session_data["payment_data"]["mobile_model_id"] = mobile_model_id
        session_data["payment_data"]["device_id"] = session.machine_id
        session_data["payment_data"]["pay_type"] = 5  # Vending machine payment
        session_data["payment_data"]["mobile_shell_id"] = mobile_shell_id
        
        # Store order information
        session_data.update(order_info)  # Add order response data
        session_data["chinese_third_id"] = third_id
        session_data["payment_initiated_at"] = datetime.now(timezone.utc).isoformat()
        session_data["chinese_response"] = chinese_response
        
        # Session is already updated above with order completion status
        session.session_data = session_data
        db.commit()
        
        return {
            "success": True,
            "message": "Payment and order completed successfully",
            "session_id": session_id,
            "third_id": third_id,
            "order_third_id": order_third_id,
            "payment_amount": payment_amount,
            "mobile_model_id": mobile_model_id,
            "device_id": session.machine_id,
            "queue_number": queue_number,
            "chinese_order_id": chinese_order_id,
            "chinese_response": chinese_response,
            "order_response": order_response
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
        print(f"=== REGISTER USER WITH SESSION START ===")
        print(f"Session ID: {session_id}")
        print(f"Request: {request.dict()}")
        
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
            # Update session status to expired
            session.status = "expired"
            db.commit()
            # Decrement machine session count
            security_manager.decrement_machine_sessions(session.machine_id)
            raise HTTPException(
                status_code=410, 
                detail="Vending session has expired. Please rescan the QR code to start a new session."
            )
        
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
        
        print(f"Successfully registered user with session:")
        print(f"- Session ID: {session_id}")
        print(f"- Machine: {session.machine_id}")
        print(f"- User Progress: {session.user_progress}")
        print(f"=== REGISTER USER WITH SESSION END ===")
        
        return {
            "success": True,
            "session_id": session_id,
            "machine_info": {
                "id": session.machine_id,
                "name": session.vending_machine.name if session.vending_machine else "Unknown",
                "location": session.vending_machine.location if session.vending_machine else location
            },
            "expires_at": session.expires_at.isoformat(),
            "user_progress": session.user_progress,
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

@router.post("/session/{session_id}/order-summary")
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
        
        # Validate order data size (increased limit to accommodate order metadata)
        if not security_manager.validate_json_size(request.order_data, 500):
            raise HTTPException(status_code=400, detail="Order data too large (max 500KB)")
        
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
        
        # Enhance order data with Chinese API requirements
        enhanced_order_data = request.order_data.copy()
        
        # Ensure we have the Chinese model ID for future orderData call
        if not enhanced_order_data.get('chinese_model_id'):
            # Try to find Chinese model ID from brand/model info
            brand_name = enhanced_order_data.get('brand', '')
            model_name = enhanced_order_data.get('model', '')
            
            # Look up Chinese model ID from database
            if brand_name and model_name:
                try:
                    from db_services import BrandService, PhoneModelService
                    brand = BrandService.get_brand_by_name(db, brand_name)
                    if brand:
                        model = PhoneModelService.get_model_by_name(db, model_name, brand.id)
                        if model and model.chinese_model_id:
                            enhanced_order_data['chinese_model_id'] = model.chinese_model_id
                            print(f"Found Chinese model ID: {model.chinese_model_id}")
                        else:
                            print(f"WARNING: No Chinese model ID found for {brand_name} {model_name}")
                    else:
                        print(f"WARNING: Brand not found: {brand_name}")
                except Exception as e:
                    print(f"WARNING: Failed to lookup Chinese model ID: {str(e)}")
        
        # Ensure device_id is available for orderData call
        if not enhanced_order_data.get('device_id'):
            enhanced_order_data['device_id'] = session.machine_id
        
        session_data.update({
            "order_summary": enhanced_order_data,
            "payment_amount": request.payment_amount,
            "currency": currency,
            "payment_requested_at": datetime.now(timezone.utc).isoformat(),
            "order_security_info": security_info
        })
        
        # CRITICAL: Store final image URL if provided for future orderData call
        if 'finalImagePublicUrl' in enhanced_order_data:
            session_data['final_image_url'] = enhanced_order_data['finalImagePublicUrl']
            print(f"DEBUG: Stored final image URL in session: {enhanced_order_data['finalImagePublicUrl']}")
        
        # IMPORTANT: SQLAlchemy doesn't detect changes to mutable JSON objects
        # We need to mark the attribute as changed to trigger persistence
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

@router.post("/session/{session_id}/confirm-payment")
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
        
        # Update session with payment confirmation
        session.status = "payment_completed"
        session.payment_method = "vending_machine"
        session.payment_confirmed_at = datetime.now(timezone.utc)
        session.last_activity = datetime.now(timezone.utc)
        
        # Store payment details with security info
        session_data = session.session_data or {}
        session_data.update({
            "payment_confirmed_at": datetime.now(timezone.utc).isoformat(),
            "payment_method": request.payment_method,
            "transaction_id": request.transaction_id,
            "payment_data": request.payment_data or {},
            "payment_security_info": security_info,
            "payment_amount_verified": request.payment_amount
        })
        session.session_data = session_data
        
        # Decrement machine session count as payment is complete
        security_manager.decrement_machine_sessions(session.machine_id)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Payment confirmed successfully",
            "session_id": session_id,
            "transaction_id": request.transaction_id,
            "status": "payment_completed",
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm payment: {str(e)}")

@router.post("/session/{session_id}/validate")
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

@router.get("/session/{session_id}/order-info")
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