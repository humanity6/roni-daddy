"""Chinese Manufacturer API routes"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from database import get_db
from backend.schemas.chinese_api import (
    OrderStatusUpdateRequest, PrintCommandRequest, 
    ChinesePayStatusRequest, ChinesePaymentDataRequest
)
from backend.services.file_service import generate_uk_download_url, generate_secure_download_token
from backend.utils.helpers import generate_third_id, get_mobile_model_id
from security_middleware import validate_relaxed_api_security, security_manager
from db_services import OrderService, OrderImageService
from models import Order, PhoneModel, VendingMachine
from datetime import datetime, timezone
import time
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chinese")

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
    request: OrderStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """Receive order status updates from Chinese manufacturers"""
    try:
        # Validate order exists
        order = OrderService.get_order_by_id(db, request.order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order not found: {request.order_id}")
        
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
    request: ChinesePayStatusRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Receive payment status updates from Chinese systems - matches their API specification"""
    try:
        # Use relaxed security for all users
        security_info = validate_relaxed_api_security(http_request)
        print(f"Payment status update from {security_info['client_ip']}: {request.third_id} -> status {request.status}")
        # Find order by third_party_payment_id
        order = db.query(Order).filter(Order.third_party_payment_id == request.third_id).first()
        
        if not order:
            # If order not found by third_id, just record the payment status without creating an order
            # This allows Chinese system to send payment status before order creation
            # The payment status will be linked when the actual order is created
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
        # Find order by third_party_payment_id
        order = db.query(Order).filter(Order.third_party_payment_id == third_id).first()
        
        if not order:
            return {
                "success": False,
                "error": "Payment record not found",
                "third_id": third_id,
                "status": 1  # Default to waiting
            }
        
        return {
            "success": True,
            "third_id": third_id,
            "status": order.chinese_payment_status,
            "order_id": order.id,
            "payment_status": order.payment_status,
            "total_amount": float(order.total_amount),
            "currency": order.currency,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None
        }
        
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