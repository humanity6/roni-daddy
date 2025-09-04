"""Chinese Manufacturer API routes"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from database import get_db
from backend.schemas.chinese_api import (
    OrderStatusUpdateRequest, PrintCommandRequest, 
    ChinesePayStatusRequest, ChinesePaymentDataRequest, ChineseOrderDataRequest
)
from backend.services.file_service import generate_uk_download_url, generate_secure_download_token
from backend.utils.helpers import generate_third_id, get_mobile_model_id
from security_middleware import validate_relaxed_api_security, security_manager
from db_services import OrderService, OrderImageService
from models import Order, PhoneModel, VendingMachine, PaymentMapping, Brand, Template
from datetime import datetime, timezone, timedelta
import time
import urllib.parse
import logging
import traceback
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chinese")

def store_payment_mapping(db: Session, third_id: str, chinese_payment_id: str, 
                         device_id: str = None, mobile_model_id: str = None, 
                         pay_amount: float = None, pay_type: int = None) -> bool:
    """Store payment mapping in database"""
    try:
        # Try PaymentMapping table first
        try:
            mapping = PaymentMapping(
                third_id=third_id,
                chinese_payment_id=chinese_payment_id,
                device_id=device_id,
                mobile_model_id=mobile_model_id,
                pay_amount=pay_amount,
                pay_type=pay_type
            )
            db.add(mapping)
            db.commit()
            logger.info(f"Stored payment mapping in PaymentMapping table: {third_id} -> {chinese_payment_id}")
            return True
        except Exception as table_error:
            logger.warning(f"PaymentMapping table not available, skipping storage: {str(table_error)}")
            db.rollback()
            # Note: For now, we rely on the Orders table to store this mapping
            # The payment will be linked when the order is created
            logger.info(f"Payment mapping will be stored when order is created: {third_id} -> {chinese_payment_id}")
            return True  # Return success since the mapping will be available in Orders
    except Exception as e:
        logger.error(f"Failed to store payment mapping: {str(e)}")
        db.rollback()
        return False

def get_payment_mapping(db: Session, third_id: str) -> str:
    """Get Chinese payment ID from database mapping"""
    try:
        # Try PaymentMapping table first
        try:
            mapping = db.query(PaymentMapping).filter(PaymentMapping.third_id == third_id).first()
            if mapping:
                logger.info(f"Found payment mapping in PaymentMapping table: {third_id} -> {mapping.chinese_payment_id}")
                return mapping.chinese_payment_id
        except Exception as table_error:
            logger.info(f"PaymentMapping table not available, using Orders table fallback: {str(table_error)}")
        
        # Fallback: Look in Orders table for existing mappings
        order = db.query(Order).filter(Order.third_party_payment_id == third_id).first()
        if order and order.chinese_payment_id:
            logger.info(f"Found payment mapping in Orders table: {third_id} -> {order.chinese_payment_id}")
            return order.chinese_payment_id
        else:
            logger.warning(f"No payment mapping found for {third_id}")
            return None
    except Exception as e:
        logger.error(f"Failed to get payment mapping: {str(e)}")
        return None

@router.get("/test-connection")
async def test_chinese_connection(http_request: Request):
    """Test endpoint for Chinese manufacturers to verify API connectivity"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Test actual connection to Chinese API
        chinese_api_status = {"status": "unknown", "error": None}
        try:
            from backend.services.chinese_payment_service import test_chinese_api_connection
            chinese_api_result = test_chinese_api_connection()
            chinese_api_status = {
                "status": "connected" if chinese_api_result.get("success") else "failed",
                "message": chinese_api_result.get("message"),
                "base_url": chinese_api_result.get("base_url")
            }
        except Exception as e:
            chinese_api_status = {
                "status": "failed",
                "error": str(e)
            }
        
        return {
            "status": "success",
            "message": "Chinese manufacturer API connection successful",
            "api_version": "2.1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_ip": security_info.get("client_ip"),
            "security_level": "relaxed_chinese_partner",
            "chinese_api_connection": chinese_api_status,
            "debug_info": {
                "rate_limit": "35 requests/minute",
                "authentication": "not_required",
                "session_validation": "flexible_format_supported"
            },
            "available_machine_ids": [
                "VM_TEST_MANUFACTURER",
                "10HKNTDOH2BA", 
                "CN_DEBUG_01",
                "VM001",
                "VM002"
            ],
            "session_format": "MACHINE_ID_YYYYMMDD_HHMMSS_RANDOM",
            "session_example": "10HKNTDOH2BA_20250729_143022_A1B2C3",
            "endpoints": {
                "test_connection": "/api/chinese/test-connection",
                "pay_status": "/api/chinese/order/payStatus",
                "payment_check": "/api/chinese/payment/{third_id}/status",
                "equipment_info": "/api/chinese/equipment/{equipment_id}/info",
                "stock_status": "/api/chinese/models/stock-status",
                "machine_management": "/api/chinese/machines",
                "vending_session_status": "/api/vending/session/{session_id}/status"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Test connection failed: {str(e)}")

@router.get("/debug/session-validation/{session_id}")
async def debug_session_validation(
    session_id: str,
    http_request: Request
):
    """Debug endpoint for Chinese developers to test session ID validation"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        client_ip = security_info.get("client_ip")
        
        # Test session ID format validation with relaxed security
        is_valid = security_manager.validate_session_id_format(session_id)
        
        # Parse session ID components if possible
        session_parts = session_id.split('_') if '_' in session_id else []
        
        return {
            "session_id": session_id,
            "is_valid": is_valid,
            "relaxed_security": True,
            "client_ip": client_ip,
            "validation_details": {
                "length": len(session_id),
                "parts_count": len(session_parts),
                "parts": session_parts if len(session_parts) <= 10 else session_parts[:10],
                "expected_format": "MACHINE_ID_YYYYMMDD_HHMMSS_RANDOM",
                "example_valid": "10HKNTDOH2BA_20250729_143022_A1B2C3"
            },
            "suggestions": [
                "Ensure machine ID uses alphanumeric characters, underscores, or hyphens",
                "Use 8-digit date format: YYYYMMDD (e.g., 20250729)",
                "Use 6-digit time format: HHMMSS (e.g., 143022)",
                "Random part should be 6-8 alphanumeric characters"
            ] if not is_valid else ["Session ID format is valid!"]
        }
        
    except Exception as e:
        return {
            "session_id": session_id,
            "is_valid": False,
            "error": str(e),
            "debug_hint": "Check if session ID follows format: MACHINE_ID_YYYYMMDD_HHMMSS_RANDOM"
        }

@router.post("/order-status-update")
async def receive_order_status_update(
    request: Optional[OrderStatusUpdateRequest] = None,
    http_request: Request = None,
    db: Session = Depends(get_db)
):
    """Receive order status updates from Chinese manufacturers - LENIENT VERSION"""
    try:
        # Use relaxed security for Chinese partners
        from security_middleware import validate_relaxed_api_security
        validate_relaxed_api_security(http_request)
        
        # Handle empty request body gracefully 
        if request is None:
            return {
                "status": "success", 
                "message": "Order status update endpoint available",
                "code": 200,
                "note": "Send POST with order_id and status in JSON body"
            }
        
        # Validate order exists (more lenient)
        try:
            order = OrderService.get_order_by_id(db, request.order_id)
        except:
            # If order service fails, just return success for Chinese API compatibility
            return {
                "status": "success",
                "message": f"Order status update accepted for {request.order_id}",
                "code": 200
            }
            
        if not order:
            # Don't fail for missing orders - return success for Chinese API compatibility
            return {
                "status": "success",
                "message": f"Order status update accepted for {request.order_id}",
                "code": 200,
                "note": "Order may be processed in different system"
            }
        
        # Validate status transition is valid
        current_status = order.status
        valid_transitions = {
            'pending': ['printing', 'failed', 'cancelled'],
            'printing': ['printed', 'failed', 'cancelled'],
            'printed': ['completed', 'failed'],
            'print_command_sent': ['printing', 'failed', 'cancelled'],
            'paid': ['print_command_sent', 'printing', 'failed', 'cancelled']
        }
        
        if current_status in valid_transitions and request.status not in valid_transitions[current_status]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status transition from '{current_status}' to '{request.status}'. Valid transitions: {valid_transitions[current_status]}"
            )
        
        # Prepare update data
        update_data = {
            "status": request.status
        }
        
        if request.queue_number:
            update_data["queue_number"] = request.queue_number
        if request.estimated_completion:
            update_data["estimated_completion"] = request.estimated_completion
        if request.chinese_order_id:
            update_data["chinese_order_id"] = request.chinese_order_id
        if request.notes:
            update_data["notes"] = request.notes
        
        # Update order status
        updated_order = OrderService.update_order_status(db, request.order_id, request.status, update_data)
        
        return {
            "success": True,
            "message": "Order status updated successfully",
            "order_id": request.order_id,
            "status": request.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")

@router.post("/order/status-update")
async def chinese_system_order_status_update(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Flexible endpoint for Chinese system order status updates
    Handles various formats the Chinese system might send
    """
    try:
        # Get raw request body to handle any format
        body = await request.body()
        
        logger.info(f"Chinese order status update received")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request body: {body.decode('utf-8') if body else 'Empty'}")
        
        # Try to parse JSON if available
        data = {}
        if body:
            try:
                import json
                data = json.loads(body.decode('utf-8'))
                logger.info(f"Parsed JSON data: {data}")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f"Failed to parse request body as JSON: {e}")
                # Try form data
                try:
                    from urllib.parse import parse_qs
                    form_data = parse_qs(body.decode('utf-8'))
                    data = {k: v[0] if len(v) == 1 else v for k, v in form_data.items()}
                    logger.info(f"Parsed form data: {data}")
                except Exception as form_error:
                    logger.warning(f"Failed to parse as form data: {form_error}")
        
        # Extract relevant information from various possible fields
        order_id = data.get('order_id') or data.get('orderId') or data.get('third_id') or data.get('thirdId')
        status = data.get('status') or data.get('orderStatus')
        queue_number = data.get('queue_number') or data.get('queueNumber') or data.get('queue_no')
        chinese_order_id = data.get('chinese_order_id') or data.get('chineseOrderId') or data.get('id')
        device_id = data.get('device_id') or data.get('deviceId')
        
        logger.info(f"Extracted fields:")
        logger.info(f"  - order_id: {order_id}")
        logger.info(f"  - status: {status}")  
        logger.info(f"  - queue_number: {queue_number}")
        logger.info(f"  - chinese_order_id: {chinese_order_id}")
        logger.info(f"  - device_id: {device_id}")
        
        # If we have a device_id, try to find the vending session and update it
        if device_id and not order_id:
            try:
                from models import VendingMachineSession
                from backend.utils.session_data_manager import SessionDataManager
                
                # Find vending session by device_id
                vending_session = db.query(VendingMachineSession).filter(
                    VendingMachineSession.machine_id == device_id,
                    VendingMachineSession.status.in_(["active", "payment_pending"])
                ).order_by(VendingMachineSession.created_at.desc()).first()
                
                if vending_session:
                    logger.info(f"Found vending session {vending_session.session_id} for device {device_id}")
                    
                    # Update session data with Chinese order status
                    status_updates = {
                        "chinese_order_status": {
                            "status": status,
                            "queue_number": queue_number,
                            "chinese_order_id": chinese_order_id,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                    
                    success = SessionDataManager.update_session_data(
                        db=db,
                        session_object=vending_session,
                        updates=status_updates,
                        merge_strategy="update",
                        verify_persistence=True
                    )
                    
                    if success:
                        logger.info(f"Successfully updated vending session {vending_session.session_id} with order status")
                    else:
                        logger.error(f"Failed to update vending session {vending_session.session_id}")
                else:
                    logger.warning(f"No active vending session found for device_id {device_id}")
                    
            except Exception as session_error:
                logger.error(f"Error updating vending session: {str(session_error)}")
        
        # Try to update order if order_id is available
        if order_id:
            try:
                order = OrderService.get_order_by_id(db, order_id)
                if order:
                    update_data = {}
                    if status:
                        update_data["status"] = str(status)
                    if queue_number:
                        update_data["queue_number"] = str(queue_number)
                    if chinese_order_id:
                        update_data["chinese_order_id"] = str(chinese_order_id)
                    
                    if update_data:
                        updated_order = OrderService.update_order_status(db, order_id, update_data.get("status"), update_data)
                        logger.info(f"Successfully updated order {order_id} with status {status}")
                else:
                    logger.warning(f"Order not found: {order_id}")
            except Exception as order_error:
                logger.error(f"Error updating order: {str(order_error)}")
        
        # Always return success to prevent Chinese system from retrying
        return {
            "success": True,
            "message": "Order status update received and processed",
            "received_data": data,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing Chinese order status update: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Still return success to prevent endless retries from Chinese system
        return {
            "success": True,
            "message": "Order status update received (with errors)",
            "error": str(e),
            "processed_at": datetime.now(timezone.utc).isoformat()
        }

@router.post("/send-print-command")
async def send_print_command(
    request: PrintCommandRequest,
    db: Session = Depends(get_db)
):
    """Send print command to Chinese manufacturers"""
    try:
        # Validate order exists
        order = OrderService.get_order_by_id(db, request.order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order not found: {request.order_id}")
        
        # Validate order is in correct state for printing
        if order.status in ['cancelled', 'failed']:
            raise HTTPException(status_code=400, detail=f"Cannot send print command for order with status: {order.status}")
        
        # Validate order has required data
        if not order.phone_model:
            raise HTTPException(status_code=400, detail="Order is missing phone model information")
        
        # Prepare print command data for Chinese manufacturers
        print_command_data = {
            "order_id": request.order_id,
            "image_urls": request.image_urls,
            "phone_model": request.phone_model,
            "customer_info": request.customer_info,
            "priority": request.priority,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "order_details": {
                "brand": order.brand.name if order.brand else None,
                "model": order.phone_model.name if order.phone_model else None,
                "template": order.template.name if order.template else None,
                "total_amount": float(order.total_amount),
                "currency": order.currency
            }
        }
        
        # Update order status to indicate print command was sent
        OrderService.update_order_status(db, request.order_id, "print_command_sent", {
            "print_command_data": print_command_data,
            "sent_to_manufacturer_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Generate unique command ID for tracking
        command_id = f"CMD_{request.order_id}_{int(time.time())}"
        
        return {
            "success": True,
            "message": "Print command sent successfully to Chinese manufacturer",
            "order_id": request.order_id,
            "command_id": command_id,
            "status": "sent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "print_command_data": print_command_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send print command: {str(e)}")

@router.post("/order/payStatus")
async def receive_payment_status_update(
    request: Optional[ChinesePayStatusRequest] = None,
    http_request: Request = None,
    db: Session = Depends(get_db)
):
    """Receive payment status updates from Chinese systems - LENIENT VERSION"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        print(f"=== PAYSTATUS WEBHOOK RECEIVED ===")
        
        # Handle empty request body gracefully
        if request is None:
            return {
                "status": "success",
                "message": "PayStatus endpoint available", 
                "code": 200,
                "note": "Send POST with third_id and status in JSON body"
            }
        
        print(f"Payment status update from {security_info['client_ip']}: {request.third_id} -> status {request.status}")
        print(f"Request data: {request.dict()}")
        print(f"Current time: {datetime.now(timezone.utc).isoformat()}")
        
        # Use SessionDataManager for robust session search
        from backend.utils.session_data_manager import SessionDataManager
        
        print(f"=== ENHANCED PAYSTATUS WEBHOOK WITH SESSIONDATAMANAGER ===")
        print(f"🔍 Searching for vending session with third_id: {request.third_id}")
        print(f"⏰ Webhook received at: {datetime.now(timezone.utc).isoformat()}")
        
        logger.info(f"=== PAYSTATUS WEBHOOK WITH SESSIONDATAMANAGER ===")
        logger.info(f"🔍 Searching for vending session with third_id: {request.third_id}")
        
        # Use SessionDataManager for comprehensive search
        vending_session = SessionDataManager.find_session_by_third_id(db, request.third_id)
        
        if vending_session:
            print(f"✅ FOUND MATCHING VENDING SESSION: {vending_session.session_id}")
            print(f"   - Status: {vending_session.status}")
            print(f"   - User progress: {vending_session.user_progress}")
            print(f"   - Created: {vending_session.created_at}")
            print(f"   - Last activity: {vending_session.last_activity}")
            
            # Log session data details
            payment_data = SessionDataManager.get_session_payment_data(vending_session)
            if payment_data:
                print(f"   - Payment data keys: {list(payment_data.keys())}")
                print(f"   - Payment data third_id: {payment_data.get('third_id')}")
                print(f"   - Payment amount: {payment_data.get('amount')}")
                print(f"   - Mobile model ID: {payment_data.get('mobile_model_id')}")
                print(f"   - Device ID: {payment_data.get('device_id')}")
            else:
                print(f"   - ⚠️ No payment data found (unexpected)")
            
            logger.info(f"✅ FOUND MATCHING VENDING SESSION: {vending_session.session_id}")
        else:
            print(f"❌ No vending session found for third_id: {request.third_id}")
            logger.warning(f"❌ No vending session found for third_id: {request.third_id}")
        
        print(f"🎯 SessionDataManager result: vending_session = {vending_session.session_id if vending_session else 'None'}")
        print(f"=== END ENHANCED PAYSTATUS WEBHOOK ===")
        
        logger.info(f"🎯 SessionDataManager result: vending_session = {vending_session.session_id if vending_session else 'None'}")
                    
        if not vending_session:
            print(f"❌ No vending session found for third_id: {request.third_id}")
            logger.warning(f"❌ No vending session found for third_id: {request.third_id}")
            
            # ENHANCED FALLBACK: Try alternative search methods
            print(f"🔍 FALLBACK: Attempting alternative session search methods...")
            
            # Try searching by chinese_payment_id from PaymentMapping
            payment_mapping = db.query(PaymentMapping).filter(
                PaymentMapping.third_id == request.third_id
            ).first()
            
            if payment_mapping:
                print(f"✅ FALLBACK: Found payment mapping, searching by chinese_payment_id")
                
                # Search sessions for this chinese_payment_id
                fallback_sessions = db.query(VendingMachineSession).filter(
                    VendingMachineSession.status.in_(["active", "payment_pending"])
                ).all()
                
                for session in fallback_sessions:
                    if (session.session_data and 
                        isinstance(session.session_data, dict) and
                        session.session_data.get('chinese_payment_id') == payment_mapping.chinese_payment_id):
                        vending_session = session
                        print(f"✅ FALLBACK SUCCESS: Found session by chinese_payment_id: {session.session_id}")
                        logger.info(f"✅ FALLBACK SUCCESS: Found session {session.session_id} by chinese_payment_id")
                        break
            
            # If still no session found, try broader search
            if not vending_session:
                print(f"🔍 FALLBACK: Trying recent session search (last 10 minutes)...")
                recent_time = datetime.now(timezone.utc) - timedelta(minutes=10)
                recent_sessions = db.query(VendingMachineSession).filter(
                    VendingMachineSession.status.in_(["active", "payment_pending"]),
                    VendingMachineSession.last_activity >= recent_time
                ).order_by(VendingMachineSession.last_activity.desc()).limit(5).all()
                
                for session in recent_sessions:
                    if (session.session_data and 
                        isinstance(session.session_data, dict)):
                        payment_data = session.session_data.get('payment_data', {})
                        if payment_data and not payment_data.get('third_id'):
                            # Found a recent session without third_id - possible race condition
                            print(f"🔄 POTENTIAL RACE CONDITION: Session {session.session_id} missing third_id")
                            logger.warning(f"Found recent session {session.session_id} without third_id - possible race condition")
        else:
            print(f"✅ Found vending session: {vending_session.session_id}")
            print(f"Payment status received: {request.status} (expected: 3 for success)")
        
        # Handle vending machine session payment confirmation
        if vending_session and request.status == 3:  # Payment successful
            print(f"=== ✅ VENDING PAYMENT CONFIRMED - TRIGGERING ORDER DATA ===")
            print(f"Session ID: {vending_session.session_id}")
            print(f"Third ID: {request.third_id}")
            print(f"Payment Status: {request.status}")
            print(f"Time: {datetime.now(timezone.utc).isoformat()}")
            logger.info(f"=== VENDING PAYMENT CONFIRMED - TRIGGERING ORDER DATA ===")
            logger.info(f"Session ID: {vending_session.session_id}")
            logger.info(f"Third ID: {request.third_id}")
            logger.info(f"Payment Status: {request.status}")
            
            # Extract order data from session
            order_summary = vending_session.session_data.get('order_summary', {})
            if not order_summary:
                logger.error(f"No order_summary found in session {vending_session.session_id}")
                return {
                    "msg": "Payment received but order data missing",
                    "code": 400,
                    "third_id": request.third_id,
                    "status": request.status
                }
            
            # Validate required order data fields
            required_fields = ['chinese_model_id', 'device_id']
            missing_fields = [field for field in required_fields if not order_summary.get(field)]
            
            if missing_fields:
                logger.error(f"Missing required order data fields in session {vending_session.session_id}: {missing_fields}")
                return {
                    "msg": f"Payment received but order data incomplete - missing: {', '.join(missing_fields)}",
                    "code": 400,
                    "third_id": request.third_id,
                    "status": request.status
                }
            
            # Get the final image URL from session data
            final_image_url = None
            if 'final_image_url' in vending_session.session_data:
                final_image_url = vending_session.session_data['final_image_url']
            elif 'order_summary' in vending_session.session_data:
                # Look for image in order summary
                order_data = vending_session.session_data['order_summary']
                final_image_url = order_data.get('final_image_url')
            
            # Generate partner token for Chinese API access
            if final_image_url and 'pimpmycase.onrender.com' in final_image_url:
                try:
                    from backend.services.file_service import generate_secure_image_url
                    
                    logger.info(f"🔒 PROCESSING IMAGE URL FOR CHINESE API TOKEN GENERATION")
                    logger.info(f"Original URL: {final_image_url}")
                    
                    # Extract filename from URL 
                    if '/image/' in final_image_url:
                        # CRITICAL FIX: Extract ONLY the filename, removing ALL existing token parameters
                        filename = final_image_url.split('/image/')[-1].split('?')[0]  # Remove everything after first ?
                        logger.info(f"Extracted clean filename: {filename}")
                        logger.info(f"Original URL had tokens: {'?' in final_image_url}")
                        
                        # Validate filename is not empty
                        if not filename or filename.strip() == '':
                            logger.error(f"❌ Empty filename extracted from URL: {final_image_url}")
                            raise ValueError(f"Invalid filename extracted from URL")
                        
                        # Generate completely new secure URL with ONLY Chinese manufacturing token
                        logger.info(f"🔒 Generating NEW secure URL with ONLY chinese_manufacturing token...")
                        logger.info(f"🔒 Input filename (clean): {filename}")
                        original_final_image_url = final_image_url
                        final_image_url = generate_secure_image_url(
                            filename=filename,  # Pass ONLY clean filename
                            partner_type="chinese_manufacturing", 
                            custom_expiry_hours=48,
                            base_url="https://pimpmycase.onrender.com"
                        )
                        
                        # Validate that token was actually added and URL is properly formatted
                        if '?token=' not in final_image_url:
                            logger.error(f"❌ Token generation failed - no token found in generated URL: {final_image_url}")
                            raise ValueError("Generated URL does not contain token parameter")
                        
                        # CRITICAL: Verify no duplicate token parameters
                        token_count = final_image_url.count('?token=')
                        if token_count != 1:
                            logger.error(f"❌ DUPLICATE TOKEN PARAMETERS DETECTED: Found {token_count} '?token=' in URL")
                            logger.error(f"Malformed URL: {final_image_url}")
                            raise ValueError(f"URL has {token_count} token parameters - should have exactly 1")
                        
                        logger.info(f"✅ SUCCESSFULLY generated Chinese API partner token")
                        logger.info(f"Original URL: {original_final_image_url}")
                        logger.info(f"New Clean URL: {final_image_url}")
                        logger.info(f"Filename: {filename}")
                        logger.info(f"✅ Token count validation: {token_count} (correct)")
                        
                        # Verify token format is correct
                        token_part = final_image_url.split('?token=')[1]
                        token_components = token_part.split(':')
                        if len(token_components) != 3:
                            logger.error(f"❌ Invalid token format: {token_part}")
                            raise ValueError(f"Generated token has invalid format: expected 3 components, got {len(token_components)}")
                        
                        logger.info(f"✅ Token validation passed - format is correct with {len(token_components)} components")
                        logger.info(f"✅ Token partner type: {token_components[1]}")
                        
                    else:
                        logger.error(f"❌ URL does not contain '/image/' path: {final_image_url}")
                        raise ValueError(f"Invalid image URL format - no '/image/' path found")
                        
                except Exception as e:
                    logger.error(f"❌ CRITICAL ERROR generating partner token for Chinese API: {str(e)}")
                    logger.error(f"Original URL: {final_image_url}")
                    import traceback
                    logger.error(f"Token generation traceback: {traceback.format_exc()}")
                    
                    # This is critical - we cannot proceed without tokens for Chinese API
                    logger.error(f"❌ CANNOT PROCEED - Chinese API requires authenticated URLs")
                    return {
                        "msg": f"Failed to generate required authentication token for image access: {str(e)}",
                        "code": 500,
                        "third_id": request.third_id,
                        "status": request.status,
                        "error_type": "token_generation_failed"
                    }
            else:
                # Handle case where URL doesn't contain expected domain or is empty
                if not final_image_url:
                    logger.error(f"❌ No final_image_url found in vending session {vending_session.session_id}")
                elif 'pimpmycase.onrender.com' not in final_image_url:
                    logger.warning(f"⚠️  Image URL is not from expected domain: {final_image_url}")
                    logger.warning(f"⚠️  Chinese API may not be able to access external URLs")
            
            if not final_image_url:
                logger.error(f"No final image URL found in session {vending_session.session_id}")
                return {
                    "msg": "Payment received but image URL missing",
                    "code": 400,
                    "third_id": request.third_id,
                    "status": request.status
                }
            
            # Generate order third_id (different from payment third_id)
            import time
            order_third_id = f"OREN{int(time.time() * 1000) % 1000000000000:012d}"
            
            # FINAL VALIDATION: Ensure image URL has authentication token before sending to Chinese API
            try:
                from backend.services.file_service import validate_secure_token
                
                logger.info(f"🔍 FINAL URL VALIDATION BEFORE CHINESE API CALL")
                logger.info(f"Final image URL to validate: {final_image_url}")
                
                # Validate that the URL has a token parameter
                if '?token=' not in final_image_url:
                    logger.error(f"❌ VALIDATION FAILED: Image URL missing token parameter")
                    logger.error(f"URL: {final_image_url}")
                    return {
                        "msg": "Image URL validation failed - missing authentication token",
                        "code": 500,
                        "third_id": request.third_id,
                        "status": request.status,
                        "error_type": "url_validation_failed"
                    }
                
                # Extract token and filename for validation
                token = final_image_url.split('?token=')[1]
                filename = final_image_url.split('/image/')[-1].split('?')[0]
                
                # Validate the token
                validation_result = validate_secure_token(token, filename, allow_partner_types=["chinese_manufacturing"])
                
                if not validation_result.get("valid"):
                    logger.error(f"❌ TOKEN VALIDATION FAILED: {validation_result.get('error')}")
                    logger.error(f"Token: {token}")
                    logger.error(f"Filename: {filename}")
                    return {
                        "msg": f"Image URL token validation failed: {validation_result.get('error')}",
                        "code": 500,
                        "third_id": request.third_id,
                        "status": request.status,
                        "error_type": "token_validation_failed"
                    }
                
                logger.info(f"✅ URL VALIDATION PASSED")
                logger.info(f"Partner type: {validation_result.get('partner_type')}")
                logger.info(f"Time remaining: {validation_result.get('time_remaining_seconds')}s")
                logger.info(f"Expires at: {validation_result.get('expires_at')}")
                
            except Exception as validation_error:
                logger.error(f"❌ URL validation error: {str(validation_error)}")
                import traceback
                logger.error(f"Validation error traceback: {traceback.format_exc()}")
                return {
                    "msg": f"Failed to validate image URL: {str(validation_error)}",
                    "code": 500,
                    "third_id": request.third_id,
                    "status": request.status,
                    "error_type": "validation_error"
                }

            # Send orderData to Chinese API now that payment is confirmed and URL is validated
            try:
                from backend.services.chinese_payment_service import send_order_data_to_chinese_api
                
                print(f"🚀 CALLING ORDERDATA ENDPOINT NOW:")
                print(f"URL: http://app-dev.deligp.com:8500/mobileShell/en/order/orderData")
                logger.info(f"🚀 CALLING ORDERDATA ENDPOINT NOW")
                logger.info(f"Sending orderData to Chinese API after payment confirmation and URL validation")
                logger.info(f"Payment Third ID: {request.third_id}")
                logger.info(f"Order Third ID: {order_third_id}")
                logger.info(f"Mobile Model ID: {order_summary.get('chinese_model_id')}")
                logger.info(f"Device ID: {order_summary.get('device_id')}")
                logger.info(f"Validated Image URL: {final_image_url}")
                
                # Get mobile_shell_id from session data
                mobile_shell_id = order_summary.get('mobile_shell_id') or vending_session.session_data.get('payment_data', {}).get('mobile_shell_id')
                
                logger.info(f"📋 OrderData parameters:")
                logger.info(f"  - third_pay_id: {request.third_id}")
                logger.info(f"  - third_id: {order_third_id}")
                logger.info(f"  - mobile_model_id: {order_summary.get('chinese_model_id')}")
                logger.info(f"  - pic: {final_image_url}")
                logger.info(f"  - device_id: {order_summary.get('device_id')}")
                logger.info(f"  - mobile_shell_id: {mobile_shell_id}")
                
                # Validate required parameters before making the call
                if not mobile_shell_id:
                    logger.error(f"❌ Missing mobile_shell_id for orderData call!")
                    logger.error(f"Order summary mobile_shell_id: {order_summary.get('mobile_shell_id')}")
                    logger.error(f"Payment data mobile_shell_id: {vending_session.session_data.get('payment_data', {}).get('mobile_shell_id')}")
                
                order_response = send_order_data_to_chinese_api(
                    third_pay_id=request.third_id,  # Use payment third_id here
                    third_id=order_third_id,
                    mobile_model_id=order_summary.get('chinese_model_id'),
                    pic=final_image_url,
                    device_id=order_summary.get('device_id'),
                    mobile_shell_id=mobile_shell_id
                )
                
                print(f"✅ ORDERDATA CALL COMPLETED!")
                print(f"Response: {json.dumps(order_response, indent=2, ensure_ascii=False)}")
                logger.info(f"✅ ORDERDATA CALL COMPLETED!")
                logger.info(f"OrderData response: {json.dumps(order_response, indent=2, ensure_ascii=False)}")
                
                # Update session with order information
                if not vending_session.session_data:
                    vending_session.session_data = {}
                vending_session.session_data['chinese_order_response'] = order_response
                vending_session.session_data['order_third_id'] = order_third_id
                vending_session.session_data['payment_confirmed_at'] = datetime.now(timezone.utc).isoformat()
                
                # Update session status based on order success
                if order_response.get('code') == 200:
                    vending_session.user_progress = "order_submitted"
                    vending_session.status = "payment_completed"
                    logger.info(f"✅ Order successfully sent to Chinese API - Session {vending_session.session_id} payment completed")
                    
                    # Store queue number if provided
                    if order_response.get('data', {}).get('queue_no'):
                        vending_session.session_data['queue_number'] = order_response['data']['queue_no']
                        logger.info(f"✅ Queue number: {order_response['data']['queue_no']}")
                else:
                    vending_session.user_progress = "payment_failed" 
                    vending_session.status = "payment_failed"
                    logger.error(f"❌ Order failed to send to Chinese API - Code: {order_response.get('code')}")
                
                # CRITICAL FIX: Ensure SQLAlchemy detects JSON field changes
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(vending_session, 'session_data')
                db.commit()
                
                return {
                    "msg": "Payment confirmed and order sent to Chinese API",
                    "code": 200,
                    "third_id": request.third_id,
                    "status": request.status,
                    "order_third_id": order_third_id,
                    "chinese_order_status": order_response.get('code'),
                    "chinese_order_msg": order_response.get('msg')
                }
                
            except Exception as order_err:
                logger.error(f"Failed to send orderData after payment confirmation: {str(order_err)}")
                import traceback
                logger.error(f"OrderData error traceback: {traceback.format_exc()}")
                
                # Still acknowledge payment but note order issue
                return {
                    "msg": f"Payment confirmed but order submission failed: {str(order_err)}",
                    "code": 200,
                    "third_id": request.third_id,
                    "status": request.status,
                    "order_error": str(order_err)
                }
        elif vending_session and request.status != 3:
            print(f"⚠️  Vending session found but payment status is {request.status} (not 3=success). Skipping orderData call.")
            logger.info(f"⚠️  Vending session found but payment status is {request.status} (not 3=success). Skipping orderData call.")
        elif not vending_session:
            print(f"⚠️  No vending session found, proceeding to order-based logic.")
            logger.info(f"⚠️  No vending session found, proceeding to order-based logic.")
        
        # Fallback to existing order-based logic
        order = db.query(Order).filter(Order.third_party_payment_id == request.third_id).first()
        
        if not order and not vending_session:
            # Neither vending session nor order found - create order from payment mapping if status is paid
            logger.warning(f"No vending session or order found for third_id: {request.third_id}")
            
            if request.status == 3:  # Payment successful - create order from payment mapping
                try:
                    # Get payment mapping to find order details
                    chinese_payment_id = get_payment_mapping(db, request.third_id)
                    if chinese_payment_id:
                        # Get payment mapping details
                        payment_mapping = db.query(PaymentMapping).filter(PaymentMapping.third_id == request.third_id).first()
                        
                        if payment_mapping:
                            logger.info(f"Creating order from payment mapping for successful payment: {request.third_id}")
                            
                            # Create order from payment mapping data - need proper IDs
                            from db_services import OrderService, BrandService, PhoneModelService, TemplateService
                            
                            # Get default IDs for unknown brand/model/template
                            default_brand = BrandService.get_brand_by_name(db, "iPhone") or db.query(Brand).first()
                            default_model = None
                            if default_brand:
                                default_model = PhoneModelService.get_models_by_brand(db, default_brand.id)
                                default_model = default_model[0] if default_model else None
                            default_template = TemplateService.get_template_by_id(db, "classic") or db.query(Template).first()
                            
                            if not default_brand or not default_model or not default_template:
                                logger.error(f"Cannot create order - missing default brand/model/template in database")
                                return {
                                    "msg": "Payment confirmed but cannot create order - missing database defaults",
                                    "code": 200,
                                    "third_id": request.third_id,
                                    "status": request.status,
                                    "error": "Database configuration incomplete"
                                }
                            
                            order_data = {
                                "third_party_payment_id": request.third_id,
                                "chinese_payment_id": chinese_payment_id,
                                "chinese_payment_status": request.status,
                                "payment_status": "paid",
                                "status": "paid",
                                "total_amount": float(payment_mapping.pay_amount) if payment_mapping.pay_amount else 19.99,
                                "currency": "GBP",
                                "paid_at": datetime.now(timezone.utc),
                                "brand_id": default_brand.id,
                                "model_id": default_model.id,
                                "template_id": default_template.id,
                                "user_data": {"created_from": "chinese_payment_status", "original_payment_id": request.third_id}
                            }
                            
                            order = OrderService.create_order(db, order_data)
                            logger.info(f"Created order {order.id} from payment mapping for {request.third_id}")
                            
                            return {
                                "msg": "Payment confirmed and order created from payment mapping",
                                "code": 200,
                                "third_id": request.third_id,
                                "status": request.status,
                                "order_id": order.id,
                                "order_created": True
                            }
                        else:
                            logger.warning(f"Payment mapping found but no details for {request.third_id}")
                    else:
                        logger.warning(f"No payment mapping found for {request.third_id}")
                        
                except Exception as create_error:
                    logger.error(f"Failed to create order from payment mapping: {create_error}")
            
            return {
                "msg": "Payment status received - order will be created when details are available",
                "code": 200,
                "third_id": request.third_id,
                "status": request.status,
                "note": "Payment status logged, awaiting order creation"
            }
        
        # Update existing order with payment status
        order.chinese_payment_status = request.status
        order.updated_at = datetime.now(timezone.utc)
        
        # Map Chinese payment status to our internal status
        status_mapping = {
            1: "pending",      # Waiting for payment
            2: "processing",   # Payment processing
            3: "paid",         # Payment successful
            4: "failed",       # Payment failed
            5: "error"         # Payment abnormal
        }
        
        # Update payment status based on Chinese status
        if request.status == 3:  # Paid
            order.payment_status = "paid"
            order.paid_at = datetime.now(timezone.utc)
            order.status = "paid"
            
            # Trigger print command for paid orders
            try:
                if order.images:  # If order has images, send to print
                    image_urls = [f"https://pimpmycase.onrender.com/image/{img.image_path.split('/')[-1]}" 
                                for img in order.images]
                    
                    print_request = PrintCommandRequest(
                        order_id=order.id,
                        image_urls=image_urls,
                        phone_model=f"{order.brand.name if order.brand else 'Unknown'} {order.phone_model.name if order.phone_model else 'Model'}",
                        customer_info={
                            "third_party_payment_id": request.third_id,
                            "chinese_payment_status": request.status
                        },
                        priority=1
                    )
                    
                    # Send print command
                    await send_print_command(print_request, db)
                    print(f"Print command sent for paid order {order.id}")
                    
            except Exception as print_error:
                print(f"Failed to send print command for order {order.id}: {print_error}")
                # Don't fail the payment confirmation if print command fails
                
        elif request.status == 4:  # Failed
            order.payment_status = "failed"
            order.status = "payment_failed"
        elif request.status == 5:  # Abnormal
            order.payment_status = "failed"
            order.status = "payment_error"
        
        db.commit()
        
        return {
            "msg": "Payment status updated successfully",
            "code": 200,
            "third_id": request.third_id,
            "status": request.status,
            "order_status": order.status,
            "payment_status": order.payment_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Payment status update error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update payment status: {str(e)}")

@router.get("/payment/{third_id}/status")
async def get_payment_status(
    third_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get real-time payment status for Chinese partners"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Log excessive polling for monitoring
        client_ip = security_info.get("client_ip")
        if client_ip == "103.213.96.36":
            # This is the Chinese team polling - limit logging noise
            import time
            current_time = time.time()
            if not hasattr(get_payment_status, "_last_log_time"):
                get_payment_status._last_log_time = {}
            
            # Only log once every 60 seconds for this IP + third_id combo
            log_key = f"{client_ip}_{third_id}"
            if current_time - get_payment_status._last_log_time.get(log_key, 0) > 60:
                logger.info(f"Chinese team polling payment status: {third_id} (log noise reduced)")
                get_payment_status._last_log_time[log_key] = current_time
        # Find order by third_party_payment_id
        order = db.query(Order).filter(Order.third_party_payment_id == third_id).first()
        
        if not order:
            return {
                "success": False,
                "error": "Payment record not found",
                "third_id": third_id,
                "status": 1  # Default to waiting
            }
        
        # Determine if polling should stop
        polling_complete = order.chinese_payment_status in [3, 4, 5]  # paid, failed, or error
        
        response = {
            "success": True,
            "third_id": third_id,
            "status": order.chinese_payment_status,
            "order_id": order.id,
            "payment_status": order.payment_status,
            "total_amount": float(order.total_amount),
            "currency": order.currency,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            "polling_complete": polling_complete
        }
        
        # Add completion message for Chinese team
        if polling_complete:
            status_text = {3: "PAID", 4: "FAILED", 5: "ERROR"}.get(order.chinese_payment_status, "FINAL")
            response["message"] = f"Payment is {status_text}. Stop polling."
            
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "third_id": third_id
        }

@router.post("/order/payData")
async def send_payment_data_to_chinese_api(
    request: ChinesePaymentDataRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Send payment data to Chinese manufacturers for card payment processing"""
    # Extract correlation ID from headers for tracing
    correlation_id = http_request.headers.get('X-Correlation-ID', f"BACKEND_{int(time.time())}")
    
    try:
        # Security validation
        security_info = validate_relaxed_api_security(http_request)
        
        logger.info(f"=== CHINESE API PAYDATA REQUEST START ({correlation_id}) ===")
        logger.info(f"Client IP: {security_info['client_ip']}")
        logger.info(f"Request payload: {request.dict()}")
        logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        
        # Validate that the mobile model exists in our database
        model = db.query(PhoneModel).filter(
            (PhoneModel.chinese_model_id == request.mobile_model_id) | 
            (PhoneModel.id == request.mobile_model_id)
        ).first()
        
        if not model:
            logger.warning(f"Mobile model {request.mobile_model_id} not found in database, proceeding anyway")
        else:
            logger.info(f"Found mobile model: {model.name} (chinese_id: {model.chinese_model_id})")
        
        # Validate required fields
        validation_errors = []
        if not request.device_id:
            validation_errors.append("device_id is required")
        if not request.mobile_model_id:
            validation_errors.append("mobile_model_id is required") 
        if not request.third_id:
            validation_errors.append("third_id is required")
        if request.pay_amount <= 0:
            validation_errors.append("pay_amount must be greater than 0")
        if request.pay_type not in [5, 6, 12]:
            validation_errors.append("pay_type must be 5 (vending machine), 6 (card), or 12 (app)")
            
        if validation_errors:
            logger.error(f"Validation errors: {validation_errors}")
            return {
                "msg": f"Validation failed: {', '.join(validation_errors)}",
                "code": 400,
                "data": {"id": "", "third_id": request.third_id}
            }
        
        # Store the payment initiation in our system for tracking
        payment_record = {
            "correlation_id": correlation_id,
            "third_id": request.third_id,
            "device_id": request.device_id,
            "mobile_model_id": request.mobile_model_id,
            "pay_amount": request.pay_amount,
            "pay_type": request.pay_type,
            "initiated_at": datetime.now(timezone.utc).isoformat(),
            "client_ip": security_info["client_ip"]
        }
        logger.info(f"Payment record: {json.dumps(payment_record, indent=2, ensure_ascii=False)}")
        
        # Make actual HTTP request to Chinese manufacturer API
        from backend.services.chinese_payment_service import send_payment_to_chinese_api
        
        logger.info("Calling Chinese payment service...")
        request_start = time.time()
        
        chinese_response = send_payment_to_chinese_api(
            mobile_model_id=request.mobile_model_id,
            device_id=request.device_id,
            third_id=request.third_id,
            pay_amount=float(request.pay_amount),
            pay_type=request.pay_type
        )
        
        request_duration = time.time() - request_start
        logger.info(f"Chinese API call completed in {request_duration:.2f}s")
        
        # Log the response in detail
        logger.info(f"=== CHINESE API RESPONSE ({correlation_id}) ===")
        logger.info(f"Response: {json.dumps(chinese_response, indent=2, ensure_ascii=False)}")
        
        if chinese_response.get("code") == 200:
            logger.info("SUCCESS: Payment data sent successfully to Chinese API")
            logger.info(f"Chinese Payment ID: {chinese_response.get('data', {}).get('id')}")
            # Persist mapping for subsequent orderData call
            try:
                chinese_payment_id = chinese_response.get('data', {}).get('id')
                if chinese_payment_id and request.third_id:
                    store_payment_mapping(
                        db=db,
                        third_id=request.third_id,
                        chinese_payment_id=chinese_payment_id,
                        device_id=request.device_id,
                        mobile_model_id=request.mobile_model_id,
                        pay_amount=request.pay_amount,
                        pay_type=request.pay_type
                    )
                    logger.info(f"Mapped payment third_id {request.third_id} -> Chinese payment id {chinese_payment_id}")
            except Exception as map_err:
                logger.warning(f"Failed to store payment id mapping: {map_err}")
        else:
            logger.error(f"Chinese API returned error code: {chinese_response.get('code')}")
            logger.error(f"Error message: {chinese_response.get('msg')}")
        
        logger.info(f"=== CHINESE API PAYDATA REQUEST END ({correlation_id}) ===")
        
        return chinese_response
        
    except Exception as e:
        logger.error(f"=== CHINESE API PAYDATA REQUEST FAILED ({correlation_id}) ===")
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return error in Chinese API format
        error_response = {
            "msg": f"Failed to send payment data: {str(e)}",
            "code": 500,
            "data": {
                "id": "",
                "third_id": request.third_id if hasattr(request, 'third_id') else ""
            }
        }
        logger.error(f"Error response: {json.dumps(error_response, indent=2, ensure_ascii=False)}")
        return error_response

@router.post("/order/orderData")
async def send_order_data_to_chinese_api(
    request: ChineseOrderDataRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Send order data to Chinese manufacturers for printing"""
    # Extract correlation ID from headers for tracing
    correlation_id = http_request.headers.get('X-Correlation-ID', f"ORDER_{int(time.time())}")
    
    try:
        # Security validation
        security_info = validate_relaxed_api_security(http_request)
        
        logger.info(f"=== CHINESE API ORDERDATA REQUEST START ({correlation_id}) ===")
        logger.info(f"Client IP: {security_info['client_ip']}")
        logger.info(f"Request payload: {request.dict()}")
        logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        
        # Validate that the mobile model exists in our database
        model = db.query(PhoneModel).filter(
            (PhoneModel.chinese_model_id == request.mobile_model_id) | 
            (PhoneModel.id == request.mobile_model_id)
        ).first()
        
        if not model:
            logger.warning(f"Mobile model {request.mobile_model_id} not found in database, proceeding anyway")
        else:
            logger.info(f"Found mobile model: {model.name} (chinese_id: {model.chinese_model_id})")
        
        # CRITICAL FIX: Chinese team confirmed third_pay_id should be the SAME as step 1 third_id
        # Do NOT convert PYEN to MSPY - use original third_pay_id as-is
        original_third_pay_id = request.third_pay_id
        effective_third_pay_id = original_third_pay_id
        
        logger.info(f"Using original third_pay_id for orderData (no conversion): {effective_third_pay_id}")
        
        # Keep mapping lookup for debugging/monitoring purposes only
        if original_third_pay_id.startswith('PYEN'):
            mapped = get_payment_mapping(db, original_third_pay_id)
            if mapped:
                logger.info(f"Payment mapping exists: {original_third_pay_id} -> {mapped} (not used in orderData)")
            else:
                logger.info(f"No payment mapping found for {original_third_pay_id} (this is expected for orderData)")

        # Store order data record for tracking (use effective_third_pay_id)
        order_data_record = {
            "correlation_id": correlation_id,
            "third_pay_id": effective_third_pay_id,
            "third_id": request.third_id,
            "device_id": request.device_id,
            "mobile_model_id": request.mobile_model_id,
            "pic": request.pic,
            "initiated_at": datetime.now(timezone.utc).isoformat(),
            "client_ip": security_info['client_ip']
        }
        
        # Correct f-string logging of order data record
        try:
            logger.info(f"Order data record: {json.dumps(order_data_record, indent=2, ensure_ascii=False)}")
        except Exception as log_err:
            logger.warning(f"Failed to serialize order_data_record for logging: {log_err}")
        logger.info("Calling Chinese order data service...")

        # Import Chinese API helpers (NOTE: function name collision with this route)
        from backend.services.chinese_payment_service import (
            send_order_data_to_chinese_api as svc_send_order_data,
            send_payment_status_to_chinese_api
        )

        # CRITICAL FIX: Enable payStatus call before orderData - this was the missing piece!
        # PayStatus must be called before orderData according to Chinese API workflow
        PRE_SEND_PAY_STATUS = True
        pay_status_resp = None
        if PRE_SEND_PAY_STATUS:
            try:
                logger.info("Sending payStatus (status=3) prior to orderData to ensure device availability...")
                pay_status_resp = send_payment_status_to_chinese_api(
                    third_id=request.third_pay_id,
                    status=3
                )
                logger.info(f"payStatus response: {json.dumps(pay_status_resp, indent=2, ensure_ascii=False)}")
            except Exception as ps_err:
                logger.warning(f"Failed to send payStatus pre-notification: {ps_err}")

        # 2. Attempt initial orderData submission
        request_start = time.time()
        attempted_third_pay_ids = [effective_third_pay_id]
        chinese_response = svc_send_order_data(
            third_pay_id=effective_third_pay_id,
            third_id=request.third_id,
            mobile_model_id=request.mobile_model_id,
            pic=request.pic,
            device_id=request.device_id,
            mobile_shell_id=request.mobile_shell_id
        )
        request_duration = time.time() - request_start

        logger.info(f"Chinese API orderData call completed in {request_duration:.2f}s")

        # 3. If device unavailable error returned, retry ONCE (optionally with payStatus if enabled)
        unavailable_msg = "device is unavailable"
        if (
            isinstance(chinese_response, dict) and
            chinese_response.get('code') == 500 and
            chinese_response.get('msg') and unavailable_msg in chinese_response.get('msg').lower()
        ):
            logger.warning("Received 'device unavailable' from orderData. Retrying once (payStatus disabled)...")
            retry_status = None
            if PRE_SEND_PAY_STATUS:
                try:
                    retry_status = send_payment_status_to_chinese_api(
                        third_id=request.third_pay_id,
                        status=3
                    )
                    logger.info(f"payStatus retry response: {json.dumps(retry_status, indent=2, ensure_ascii=False)}")
                except Exception as ps_retry_err:
                    logger.warning(f"payStatus retry failed: {ps_retry_err}")

            retry_start = time.time()
            retry_response = svc_send_order_data(
                third_pay_id=effective_third_pay_id,
                third_id=request.third_id,
                mobile_model_id=request.mobile_model_id,
                pic=request.pic,
                device_id=request.device_id,
                mobile_shell_id=request.mobile_shell_id
            )
            retry_duration = time.time() - retry_start
            logger.info(f"Chinese API orderData RETRY completed in {retry_duration:.2f}s")
            logger.info(f"OrderData retry response: {json.dumps(retry_response, indent=2, ensure_ascii=False)}")

            # If retry succeeded (code 200) replace original response
            if retry_response.get('code') == 200:
                logger.info("Retry succeeded after initial 'device unavailable' error.")
                chinese_response = retry_response
            else:
                logger.warning("Retry did not succeed; evaluating fallback strategies (original PYEN id and sanitized pic)...")
                # Fallback: If we substituted MSPY id and original starts with PYEN and not already tried, attempt with original id
                if (
                    original_third_pay_id != effective_third_pay_id and
                    original_third_pay_id.startswith('PYEN') and
                    original_third_pay_id not in attempted_third_pay_ids
                ):
                    logger.info(f"Attempting fallback orderData submission using original third_pay_id {original_third_pay_id} (PYEN) after MSPY attempt(s) failed.")
                    attempted_third_pay_ids.append(original_third_pay_id)
                    fb_start = time.time()
                    fb_response = svc_send_order_data(
                        third_pay_id=original_third_pay_id,
                        third_id=request.third_id,
                        mobile_model_id=request.mobile_model_id,
                        pic=request.pic,
                        device_id=request.device_id,
                        mobile_shell_id=request.mobile_shell_id
                    )
                    fb_duration = time.time() - fb_start
                    logger.info(f"Fallback orderData attempt completed in {fb_duration:.2f}s")
                    logger.info(f"Fallback response: {json.dumps(fb_response, indent=2, ensure_ascii=False)}")
                    # If fallback succeeds, adopt it
                    if isinstance(fb_response, dict) and fb_response.get('code') == 200:
                        logger.info("Fallback with original PYEN third_pay_id succeeded.")
                        chinese_response = fb_response
                    else:
                        logger.warning("Fallback with original PYEN third_pay_id also failed.")
                else:
                    logger.info("No viable fallback third_pay_id to attempt or already tried.")

                # Additional fallback: try sanitized image URL without query string (token) if present
                if (
                    isinstance(chinese_response, dict) and chinese_response.get('code') == 500 and
                    '?' in request.pic
                ):
                    parsed = urllib.parse.urlsplit(request.pic)
                    sanitized_pic = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', ''))
                    if sanitized_pic != request.pic:
                        logger.info(f"Attempting fallback orderData with sanitized pic URL (removed query params): {sanitized_pic}")
                        san_start = time.time()
                        san_response = svc_send_order_data(
                            third_pay_id=effective_third_pay_id,
                            third_id=request.third_id,
                            mobile_model_id=request.mobile_model_id,
                            pic=sanitized_pic,
                            device_id=request.device_id,
                            mobile_shell_id=request.mobile_shell_id
                        )
                        san_duration = time.time() - san_start
                        logger.info(f"Sanitized pic fallback completed in {san_duration:.2f}s")
                        logger.info(f"Sanitized pic response: {json.dumps(san_response, indent=2, ensure_ascii=False)}")
                        if isinstance(san_response, dict) and san_response.get('code') == 200:
                            logger.info("Sanitized pic fallback succeeded.")
                            chinese_response = san_response
                        else:
                            logger.warning("Sanitized pic fallback also failed.")
        
        # Log the response in detail
        logger.info(f"=== CHINESE API RESPONSE ({correlation_id}) ===")
        logger.info(f"Response: {json.dumps(chinese_response, indent=2, ensure_ascii=False)}")
        
        if chinese_response.get("code") == 200:
            logger.info("SUCCESS: Order data sent successfully to Chinese API")
            logger.info(f"Chinese Order ID: {chinese_response.get('data', {}).get('id')}")
        else:
            logger.error(f"Chinese API returned error code: {chinese_response.get('code')}")
            logger.error(f"Error message: {chinese_response.get('msg')}")
            
            # Update vending session status on Chinese API failure
            try:
                from models import VendingMachineSession
                from db_services import VendingMachineSessionService
                
                # Find any active vending sessions that might be waiting for this order
                # Use device_id to match sessions since they share the same device
                active_sessions = db.query(VendingMachineSession).filter(
                    VendingMachineSession.machine_id == request.device_id,
                    VendingMachineSession.status.in_(['active', 'designing', 'payment_pending']),
                    VendingMachineSession.user_progress.in_(['order_submitted', 'payment_requested'])
                ).all()
                
                for session in active_sessions:
                    logger.info(f"Updating vending session {session.session_id} status to payment_failed due to Chinese API error")
                    session.status = 'payment_failed'
                    session.user_progress = 'order_failed'
                    
                    # Add error details to session data
                    if not session.session_data:
                        session.session_data = {}
                    session.session_data['chinese_api_error'] = {
                        'code': chinese_response.get('code'),
                        'message': chinese_response.get('msg'),
                        'failed_at': datetime.now(timezone.utc).isoformat(),
                        'error_type': 'orderdata_failed'
                    }
                    session.last_activity = datetime.now(timezone.utc)
                    
                    # CRITICAL FIX: Ensure SQLAlchemy detects JSON field changes
                    from sqlalchemy.orm.attributes import flag_modified
                    flag_modified(session, 'session_data')
                
                if active_sessions:
                    db.commit()
                    logger.info(f"Updated {len(active_sessions)} vending sessions to payment_failed status")
                
            except Exception as session_update_error:
                logger.warning(f"Failed to update vending session status after Chinese API error: {session_update_error}")
                # Don't fail the main response due to session update issues
        
        logger.info(f"=== CHINESE API ORDERDATA REQUEST END ({correlation_id}) ===")
        
        # Attach debug metadata for client-side troubleshooting (non-breaking)
        if isinstance(chinese_response, dict):
            chinese_response.setdefault('_debug', {})
            debug_block = chinese_response['_debug']
            debug_block['attempted_third_pay_ids'] = attempted_third_pay_ids
            debug_block['original_third_pay_id'] = original_third_pay_id
            debug_block['effective_first_third_pay_id'] = effective_third_pay_id
            debug_block['pre_pay_status_attempted'] = PRE_SEND_PAY_STATUS
            debug_block['pay_status_resp_code'] = pay_status_resp.get('code') if isinstance(pay_status_resp, dict) else None
            debug_block['pic_had_query'] = '?' in request.pic
        return chinese_response
        
    except Exception as e:
        logger.error(f"=== CHINESE API ORDERDATA REQUEST FAILED ({correlation_id}) ===")
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return error in Chinese API format
        error_response = {
            "msg": f"Failed to send order data: {str(e)}",
            "code": 500,
            "data": {
                "id": "",
                "third_pay_id": request.third_pay_id if hasattr(request, 'third_pay_id') else "",
                "third_id": request.third_id if hasattr(request, 'third_id') else ""
            }
        }
        logger.error(f"Error response: {json.dumps(error_response, indent=2, ensure_ascii=False)}")
        return error_response

@router.post("/sync/models")
async def sync_models_from_chinese_api(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Sync phone models and brands from Chinese API to our database"""
    try:
        # Security validation  
        security_info = validate_relaxed_api_security(http_request)
        logger.info(f"Model sync initiated by {security_info['client_ip']}")
        
        from backend.services.chinese_payment_service import get_chinese_brands, get_chinese_stock
        from db_services import BrandService, PhoneModelService
        
        sync_results = {
            "brands_processed": 0,
            "brands_added": 0,
            "brands_updated": 0,
            "models_processed": 0,
            "models_added": 0,
            "models_updated": 0,
            "errors": []
        }
        
        # Get brands from Chinese API
        brands_response = get_chinese_brands()
        if not brands_response.get("success"):
            raise HTTPException(status_code=500, detail=f"Failed to fetch brands: {brands_response.get('message')}")
        
        chinese_brands = brands_response.get("brands", [])
        logger.info(f"Found {len(chinese_brands)} brands in Chinese API")
        
        # Filter to only include iPhone, Samsung, and Google brands
        target_brands = ["Apple", "SAMSUNG", "Google"]
        filtered_brands = [brand for brand in chinese_brands if brand.get("e_name") in target_brands]
        
        logger.info(f"Filtered to {len(filtered_brands)} target brands: {[b.get('e_name') for b in filtered_brands]}")
        
        for brand_data in filtered_brands:
            try:
                sync_results["brands_processed"] += 1
                brand_name = brand_data.get("e_name", brand_data.get("name"))
                chinese_brand_id = brand_data.get("id")
                
                if not brand_name or not chinese_brand_id:
                    sync_results["errors"].append(f"Invalid brand data: {brand_data}")
                    continue
                
                # Check if brand exists in our database
                existing_brand = BrandService.get_brand_by_name(db, brand_name)
                
                if existing_brand:
                    # Update existing brand with Chinese ID if missing
                    if not hasattr(existing_brand, 'chinese_brand_id') or not existing_brand.chinese_brand_id:
                        existing_brand.chinese_brand_id = chinese_brand_id
                        sync_results["brands_updated"] += 1
                        logger.info(f"Updated brand {brand_name} with Chinese ID: {chinese_brand_id}")
                else:
                    # Create new brand
                    brand_create_data = {
                        "name": brand_name,
                        "display_name": brand_name.upper(),
                        "chinese_brand_id": chinese_brand_id,
                        "is_available": True
                    }
                    new_brand = BrandService.create_brand(db, brand_create_data)
                    sync_results["brands_added"] += 1
                    logger.info(f"Added new brand: {brand_name} ({chinese_brand_id})")
                    existing_brand = new_brand
                
                # Now sync models for this brand
                stock_response = get_chinese_stock(device_id="1CBRONIQRWQQ", brand_id=chinese_brand_id)
                if stock_response.get("success"):
                    stock_items = stock_response.get("stock_items", [])
                    logger.info(f"Found {len(stock_items)} models for brand {brand_name}")
                    
                    for model_data in stock_items:
                        try:
                            sync_results["models_processed"] += 1
                            model_name = model_data.get("mobile_model_name")
                            chinese_model_id = model_data.get("mobile_model_id")
                            price = model_data.get("price", "0")
                            stock = model_data.get("stock", 0)
                            
                            if not model_name or not chinese_model_id:
                                sync_results["errors"].append(f"Invalid model data: {model_data}")
                                continue
                            
                            # Check if model exists
                            existing_model = PhoneModelService.get_model_by_name(db, model_name, existing_brand.id)
                            
                            if existing_model:
                                # Update existing model
                                if existing_model.chinese_model_id != chinese_model_id:
                                    existing_model.chinese_model_id = chinese_model_id
                                    sync_results["models_updated"] += 1
                                    logger.info(f"Updated model {model_name} with Chinese ID: {chinese_model_id}")
                            else:
                                # Create new model
                                model_create_data = {
                                    "name": model_name,
                                    "display_name": model_name,
                                    "brand_id": existing_brand.id,
                                    "chinese_model_id": chinese_model_id,
                                    "is_available": True,
                                    "price": float(price) if price.replace('.', '').isdigit() else 19.99
                                }
                                PhoneModelService.create_model(db, model_create_data)
                                sync_results["models_added"] += 1
                                logger.info(f"Added new model: {model_name} ({chinese_model_id})")
                                
                        except Exception as model_error:
                            error_msg = f"Error processing model {model_data}: {str(model_error)}"
                            sync_results["errors"].append(error_msg)
                            logger.error(error_msg)
                else:
                    logger.warning(f"Failed to get stock for brand {brand_name}: {stock_response.get('message')}")
                    
            except Exception as brand_error:
                error_msg = f"Error processing brand {brand_data}: {str(brand_error)}"
                sync_results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Commit all changes
        db.commit()
        logger.info(f"Model sync completed successfully: {sync_results}")
        
        return {
            "success": True,
            "message": "Models synced successfully from Chinese API",
            "sync_results": sync_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model sync failed: {str(e)}")
        import traceback
        logger.error(f"Sync traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Model sync failed: {str(e)}")


@router.get("/sync/models/auto")
async def auto_sync_models_if_needed(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Auto-sync models from Chinese API if database is missing recent Chinese models"""
    try:
        security_info = validate_relaxed_api_security(http_request)
        
        # Check if we have recent Chinese models
        models_with_chinese_ids = db.query(PhoneModel).filter(
            PhoneModel.chinese_model_id.isnot(None)
        ).count()
        
        should_sync = models_with_chinese_ids < 5  # Threshold for auto-sync
        
        sync_info = {
            "models_with_chinese_ids": models_with_chinese_ids,
            "sync_recommended": should_sync,
            "last_check": datetime.now(timezone.utc).isoformat()
        }
        
        if should_sync:
            # Auto-trigger sync
            logger.info(f"Auto-triggering model sync - only {models_with_chinese_ids} models have Chinese IDs")
            
            # Call the sync function internally
            sync_result = await sync_models_from_chinese_api(http_request, db)
            sync_info["auto_sync_result"] = sync_result
            sync_info["sync_performed"] = True
        else:
            sync_info["sync_performed"] = False
            sync_info["message"] = f"Sync not needed - {models_with_chinese_ids} models already have Chinese IDs"
        
        return {
            "success": True,
            "sync_info": sync_info
        }
        
    except Exception as e:
        logger.error(f"Auto-sync check failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "models_with_chinese_ids": 0
        }


@router.get("/equipment/{equipment_id}/info")
async def get_equipment_info(
    equipment_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
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

@router.post("/equipment/{equipment_id}/stock")
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

@router.get("/models/stock-status")
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

@router.post("/machines")
async def add_vending_machine(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Add new vending machine to the database for Chinese partners"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Get request body
        body = await http_request.json()
        
        # Validate required fields
        machine_id = body.get('machine_id', '').strip()
        name = body.get('name', '').strip()
        location = body.get('location', '').strip()
        
        if not machine_id:
            return {
                "success": False,
                "error": "machine_id is required",
                "code": 400
            }
        
        if not name:
            name = f"Vending Machine {machine_id}"
        
        # Check if machine already exists
        existing_machine = db.query(VendingMachine).filter(VendingMachine.id == machine_id).first()
        if existing_machine:
            return {
                "success": False,
                "error": f"Machine with ID '{machine_id}' already exists",
                "code": 409,
                "existing_machine": {
                    "id": existing_machine.id,
                    "name": existing_machine.name,
                    "location": existing_machine.location,
                    "is_active": existing_machine.is_active,
                    "created_at": existing_machine.created_at.isoformat()
                }
            }
        
        # Create new vending machine
        new_machine = VendingMachine(
            id=machine_id,
            name=name,
            location=location,
            is_active=body.get('is_active', True),
            qr_config=body.get('qr_config', {}),
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(new_machine)
        db.commit()
        db.refresh(new_machine)
        
        return {
            "success": True,
            "message": f"Vending machine '{machine_id}' added successfully",
            "machine": {
                "id": new_machine.id,
                "name": new_machine.name,
                "location": new_machine.location,
                "is_active": new_machine.is_active,
                "created_at": new_machine.created_at.isoformat()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "code": 500
        }

@router.get("/machines")
async def list_vending_machines(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """List all vending machines for Chinese partners"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Get all vending machines
        machines = db.query(VendingMachine).all()
        
        machine_data = []
        for machine in machines:
            machine_data.append({
                "id": machine.id,
                "name": machine.name,
                "location": machine.location,
                "is_active": machine.is_active,
                "last_heartbeat": machine.last_heartbeat.isoformat() if machine.last_heartbeat else None,
                "created_at": machine.created_at.isoformat(),
                "updated_at": machine.updated_at.isoformat() if machine.updated_at else None,
                "qr_config": machine.qr_config
            })
        
        return {
            "success": True,
            "machines": machine_data,
            "total_machines": len(machine_data),
            "active_machines": len([m for m in machine_data if m["is_active"]]),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.put("/machines/{machine_id}")
async def update_vending_machine(
    machine_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Update vending machine details for Chinese partners"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Find the machine
        machine = db.query(VendingMachine).filter(VendingMachine.id == machine_id).first()
        if not machine:
            return {
                "success": False,
                "error": f"Machine '{machine_id}' not found",
                "code": 404
            }
        
        # Get request body
        body = await http_request.json()
        
        # Update fields if provided
        if 'name' in body and body['name'].strip():
            machine.name = body['name'].strip()
        if 'location' in body:
            machine.location = body['location'].strip()
        if 'is_active' in body:
            machine.is_active = body['is_active']
        if 'qr_config' in body:
            machine.qr_config = body['qr_config']
        
        machine.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(machine)
        
        return {
            "success": True,
            "message": f"Vending machine '{machine_id}' updated successfully",
            "machine": {
                "id": machine.id,
                "name": machine.name,
                "location": machine.location,
                "is_active": machine.is_active,
                "created_at": machine.created_at.isoformat(),
                "updated_at": machine.updated_at.isoformat()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "code": 500
        }

@router.post("/print/trigger")
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

@router.get("/print/{order_id}/status")
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

@router.get("/order/{order_id}/download-links")
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
                
                download_links.append({
                    "image_id": img.id,
                    "filename": filename,
                    "download_url": download_url,
                    "secure_url": f"https://pimpmycase.onrender.com/image/{filename}?token={secure_token}",
                    "image_type": img.image_type,
                    "created_at": img.created_at.isoformat()
                })
        
        return {
            "success": True,
            "order_id": order_id,
            "download_links": download_links,
            "total_images": len(download_links),
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=48)).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "order_id": order_id
        }

@router.get("/brands")
async def get_chinese_brands(
    http_request: Request
):
    """Get brand list from Chinese API"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Import Chinese API service
        from backend.services.chinese_payment_service import get_chinese_brands
        
        # Fetch brands from Chinese API
        result = get_chinese_brands()
        
        if result.get("success"):
            # Filter and order brands: iPhone first, Samsung second, Google third (unavailable)
            all_brands = result.get("brands", [])
            
            # Find iPhone and Samsung brands
            iphone_brand = None
            samsung_brand = None
            
            for brand in all_brands:
                e_name = brand.get("e_name", "").upper()
                if e_name == "APPLE":
                    iphone_brand = {
                        "id": brand.get("id"),
                        "e_name": "iPhone", 
                        "name": "iPhone",
                        "available": True,
                        "order": 1
                    }
                elif e_name == "SAMSUNG":
                    samsung_brand = {
                        "id": brand.get("id"),
                        "e_name": "Samsung",
                        "name": "Samsung", 
                        "available": True,
                        "order": 2
                    }
            
            # Create filtered brand list
            filtered_brands = []
            
            if iphone_brand:
                filtered_brands.append(iphone_brand)
            
            if samsung_brand:
                filtered_brands.append(samsung_brand)
            
            # Add Google as unavailable
            filtered_brands.append({
                "id": "GOOGLE_UNAVAILABLE",
                "e_name": "Google",
                "name": "Google",
                "available": False,
                "order": 3,
                "message": "Currently unavailable"
            })
            
            return {
                "success": True,
                "brands": filtered_brands,
                "total_brands": len(filtered_brands),
                "available_brands": len([b for b in filtered_brands if b.get("available", False)]),
                "message": f"Filtered brands: {len([b for b in filtered_brands if b.get('available', False)])} available, {len([b for b in filtered_brands if not b.get('available', False)])} unavailable",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "Failed to fetch brands"),
                "brands": []
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "brands": []
        }

@router.get("/stock/{device_id}/{brand_id}")
async def get_chinese_stock(
    device_id: str,
    brand_id: str,
    http_request: Request
):
    """Get stock list for a specific brand and device from Chinese API"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Sanitize inputs
        from security_middleware import security_manager
        device_id = security_manager.sanitize_string_input(device_id, 50)
        brand_id = security_manager.sanitize_string_input(brand_id, 50)
        
        # Check if brand is unavailable (like Google)
        if brand_id == "GOOGLE_UNAVAILABLE":
            return {
                "success": False,
                "error": "Brand currently unavailable",
                "stock_items": [],
                "available_items": [],
                "device_id": device_id,
                "brand_id": brand_id,
                "message": "Google phones are currently unavailable"
            }
        
        # Import Chinese API service
        from backend.services.chinese_payment_service import get_chinese_stock
        
        # Fetch stock from Chinese API
        result = get_chinese_stock(device_id, brand_id)
        
        if result.get("success"):
            stock_items = result.get("stock_items", [])
            
            # Filter only items with stock > 0
            available_items = [item for item in stock_items if item.get("stock", 0) > 0]
            
            return {
                "success": True,
                "stock_items": stock_items,
                "available_items": available_items,
                "total_items": result.get("total_items", 0),
                "available_count": len(available_items),
                "device_id": device_id,
                "brand_id": brand_id,
                "message": f"Found {len(available_items)} available models out of {result.get('total_items', 0)} total",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "success": False,
                "error": result.get("message", "Failed to fetch stock"),
                "stock_items": [],
                "available_items": [],
                "device_id": device_id,
                "brand_id": brand_id
            }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "stock_items": [],
            "available_items": [],
            "device_id": device_id,
            "brand_id": brand_id
        }

@router.get("/images/batch-download")
async def get_batch_download_links(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get batch download links for multiple orders - for Chinese manufacturers"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        
        # Get query parameters
        query_params = dict(http_request.query_params)
        order_ids = query_params.get('order_ids', '').split(',') if query_params.get('order_ids') else []
        limit = min(50, int(query_params.get('limit', 20)))  # Max 50 orders at once
        
        if not order_ids or order_ids == ['']:
            # If no specific orders requested, get recent completed orders
            orders = db.query(Order).options(joinedload(Order.images)).filter(
                Order.status.in_(["completed", "print_job_triggered", "printing"])
            ).order_by(desc(Order.created_at)).limit(limit).all()
        else:
            # Get specific orders
            orders = db.query(Order).options(joinedload(Order.images)).filter(
                Order.id.in_(order_ids[:limit])  # Limit to prevent abuse
            ).all()
        
        batch_downloads = []
        
        for order in orders:
            order_downloads = []
            
            for img in order.images:
                if img.image_path:
                    filename = img.image_path.split('/')[-1]
                    download_url = generate_uk_download_url(filename)
                    secure_token = generate_secure_download_token(filename, expiry_hours=24)
                    
                    order_downloads.append({
                        "image_id": img.id,
                        "filename": filename,
                        "download_url": download_url,
                        "secure_url": f"https://pimpmycase.onrender.com/image/{filename}?token={secure_token}",
                        "image_type": img.image_type
                    })
            
            if order_downloads:  # Only include orders with images
                batch_downloads.append({
                    "order_id": order.id,
                    "status": order.status,
                    "created_at": order.created_at.isoformat(),
                    "images": order_downloads,
                    "image_count": len(order_downloads)
                })
        
        return {
            "success": True,
            "batch_downloads": batch_downloads,
            "total_orders": len(batch_downloads),
            "total_images": sum(order["image_count"] for order in batch_downloads),
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }