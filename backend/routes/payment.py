"""Payment processing API routes - Stripe integration"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from backend.schemas.payment import CheckoutSessionRequest, PaymentSuccessRequest
from backend.services.payment_service import initialize_stripe
from backend.services.chinese_payment_service import get_chinese_brands, get_chinese_stock
from db_services import OrderService, BrandService, PhoneModelService, TemplateService
from models import Brand, PhoneModel  # Added for Chinese API fallback validation
from datetime import datetime, timezone
from typing import Optional, Tuple
import stripe
import os
import time

router = APIRouter()

# Stripe is initialized in the payment service
stripe_client = initialize_stripe()


def resolve_phone_model_from_chinese_id(
    db: Session,
    chinese_model_id: str,
    device_id: Optional[str]
) -> Tuple[Brand, PhoneModel]:
    """Resolve brand and model records for a Chinese mobile_model_id using official API data."""
    if not chinese_model_id:
        raise HTTPException(status_code=400, detail="chinese_model_id is required")

    print(f"🔍 Resolving Chinese model ID: {chinese_model_id}")

    # Fast path: check if we already have the mapping stored locally
    existing_model = db.query(PhoneModel).filter(PhoneModel.chinese_model_id == chinese_model_id).first()
    if existing_model:
        brand = existing_model.brand or BrandService.get_brand_by_id(db, existing_model.brand_id)
        if not brand:
            raise HTTPException(status_code=500, detail="Local model mapping missing associated brand")
        print(f"✅ Found existing model mapping: {existing_model.name} ({existing_model.id})")
        return brand, existing_model

    if not device_id:
        raise HTTPException(
            status_code=400,
            detail="device_id is required to resolve official Chinese model data"
        )

    # Fetch official brand list directly from the Chinese API (no fallbacks)
    brand_response = get_chinese_brands()
    if not brand_response.get("success"):
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch brand list from Chinese API: {brand_response.get('message', 'Unknown error')}"
        )

    brands = brand_response.get("brands") or []
    matched_brand_data = None
    matched_stock_item = None

    for brand_data in brands:
        chinese_brand_id = brand_data.get("id")
        if not chinese_brand_id:
            continue

        stock_response = get_chinese_stock(device_id=device_id, brand_id=chinese_brand_id)
        if not stock_response.get("success"):
            print(
                f"⚠️ Chinese API stock lookup failed for brand {chinese_brand_id}: "
                f"{stock_response.get('message', 'no message')}"
            )
            continue

        for stock_item in stock_response.get("stock_items", []):
            if stock_item.get("mobile_model_id") == chinese_model_id:
                matched_brand_data = brand_data
                matched_stock_item = stock_item
                break

        if matched_stock_item:
            break

    if not matched_stock_item or not matched_brand_data:
        raise HTTPException(
            status_code=404,
            detail=f"Chinese model ID {chinese_model_id} not found in official Chinese API stock data"
        )

    brand_name = (
        matched_brand_data.get("e_name")
        or matched_brand_data.get("name")
        or matched_brand_data.get("brand_name")
    )
    if not brand_name:
        raise HTTPException(status_code=502, detail="Chinese API response missing brand name for model")

    chinese_brand_id = matched_brand_data.get("id")
    brand = BrandService.get_brand_by_name(db, brand_name)
    if brand:
        updated = False
        if chinese_brand_id and brand.chinese_brand_id != chinese_brand_id:
            brand.chinese_brand_id = chinese_brand_id
            updated = True
        if updated:
            db.commit()
            db.refresh(brand)
            print(f"✅ Updated brand {brand.name} with Chinese ID {chinese_brand_id}")
    else:
        brand_create_data = {
            "name": brand_name,
            "display_name": brand_name.upper(),
            "chinese_brand_id": chinese_brand_id,
            "is_available": True
        }
        brand = BrandService.create_brand(db, brand_create_data)
        print(f"✅ Created new brand from Chinese API: {brand.name} ({chinese_brand_id})")

    model_name = matched_stock_item.get("mobile_model_name") or matched_stock_item.get("model_name")
    if not model_name:
        raise HTTPException(status_code=502, detail="Chinese API response missing model name")

    price_value = matched_stock_item.get("price")
    if price_value is None:
        raise HTTPException(status_code=502, detail="Chinese API response missing model price")

    try:
        price_float = float(price_value)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=502,
            detail=f"Chinese API returned invalid price '{price_value}' for model {model_name}"
        )

    stock_raw = matched_stock_item.get("stock")
    try:
        stock_int = int(stock_raw) if stock_raw is not None else 0
    except (TypeError, ValueError):
        stock_int = 0

    # Re-check if any local model matches by name (legacy records without Chinese ID)
    model = db.query(PhoneModel).filter(PhoneModel.name == model_name, PhoneModel.brand_id == brand.id).first()
    if model:
        updated = False
        if model.chinese_model_id != chinese_model_id:
            model.chinese_model_id = chinese_model_id
            updated = True
        if model.brand_id != brand.id:
            model.brand_id = brand.id
            updated = True
        current_price = float(model.price) if model.price is not None else None
        if current_price is None or abs(current_price - price_float) > 0.0001:
            model.price = price_float
            updated = True
        if model.stock != stock_int:
            model.stock = stock_int
            updated = True
        if updated:
            db.commit()
            db.refresh(model)
            print(f"✅ Updated existing model {model.name} with official Chinese data")
    else:
        model_data = {
            "name": model_name,
            "display_name": model_name,
            "brand_id": brand.id,
            "price": price_float,
            "chinese_model_id": chinese_model_id,
            "stock": stock_int,
            "is_available": True
        }
        model = PhoneModelService.create_model(db, model_data)
        print(f"✅ Created new model from Chinese API: {model.name} ({chinese_model_id})")

    return brand, model

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db)
):
    """Create a Stripe Checkout session"""
    try:
        # CRITICAL FIX: Handle both amount_pence (new) and amount (legacy) to avoid floating point errors
        if hasattr(request, 'amount_pence') and request.amount_pence:
            amount_pence = int(request.amount_pence)  # Already in pence
            amount_pounds = amount_pence / 100  # For logging
        elif hasattr(request, 'amount') and request.amount:
            amount_pence = int(request.amount * 100)  # Convert pounds to pence (legacy)
            amount_pounds = request.amount
        else:
            raise ValueError("No amount or amount_pence provided")
            
        print(f"Payment amount: {amount_pounds}£ ({amount_pence} pence)")
        
        # Determine the base URL for redirects
        base_url = "https://pimpmycase.shop"  # New Hostinger Production URL
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': f'Phone Case - {request.template_id}',
                        'description': f'{request.brand} {request.model}',
                    },
                    'unit_amount': amount_pence,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{base_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{base_url}/payment-cancel',
            locale='en-GB',  # CRITICAL FIX: Set locale for GBP currency to prevent "Cannot find module './en'" error
            metadata={
                'template_id': request.template_id,
                'brand': request.brand,
                'model': request.model,
                'color': request.color
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout session creation failed: {str(e)}")

@router.get("/payment-success")
async def payment_success_page(session_id: str, db: Session = Depends(get_db)):
    """Handle payment success redirect from Stripe"""
    try:
        print(f"Payment success page accessed with session: {session_id}")
        
        # CRITICAL FIX: Remove test session handling - no mock data
        # All payments must go through proper Stripe verification
        session = stripe.checkout.Session.retrieve(session_id)
        print(f"Checkout session status: {session.payment_status}")
        
        if session.payment_status != 'paid':
            raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Get metadata from session
        template_name = session.metadata.get('template_id', 'classic')
        brand_name = session.metadata.get('brand', 'iPhone')
        model_name = session.metadata.get('model', 'iPhone 15 Pro')
        color = session.metadata.get('color', 'Natural Titanium')

        # Resolve device information early for Chinese API lookups
        device_id = request.order_data.get('device_id') or request.order_data.get('machine_id')
        
        # CRITICAL FIX: No hardcoded queue number generation - must come from Chinese API
        # This route should not generate queue numbers without Chinese API approval
        print(f"⚠️ WARNING: payment-success route called - queue numbers should come from Chinese API in process-payment-success")
        
        return {
            "success": True,
            "session_id": session_id,
            "payment_id": session.payment_intent,
            "queue_no": None,  # No hardcoded queue numbers
            "status": "paid",
            "brand": brand_name,
            "model": model_name,
            "color": color,
            "template_id": template_name,
            "amount": session.amount_total / 100,
            "note": "Use process-payment-success endpoint for Chinese API integration"
        }
        
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        print(f"Payment success error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Payment success failed: {str(e)}")

@router.post("/process-payment-success")
async def process_payment_success(
    request: PaymentSuccessRequest,
    db: Session = Depends(get_db)
):
    """Process successful payment from Stripe Checkout"""
    try:
        print(f"Starting payment processing for session: {request.session_id}")
        
        # CRITICAL FIX: Remove test session handling - no mock data
        # All payments must go through proper Stripe verification
        session = stripe.checkout.Session.retrieve(request.session_id)
            
        print(f"Checkout session status: {session.payment_status}")
        print(f"Session amount: {session.amount_total}")
        print(f"Session currency: {session.currency}")
        
        if session.payment_status != 'paid':
            raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Get metadata from session
        template_name = session.metadata.get('template_id', 'classic')
        brand_name = session.metadata.get('brand', 'iPhone')
        model_name = session.metadata.get('model', 'iPhone 15 Pro')
        color = session.metadata.get('color', 'Natural Titanium')
        
        # Find or create order from the request data
        order_id = request.order_data.get('order_id')
        if order_id:
            order = OrderService.get_order_by_id(db, order_id)
            if order:
                # Update existing order with payment info
                order.stripe_session_id = request.session_id
                order.stripe_payment_intent_id = session.payment_intent
                order.payment_status = "paid"
                order.paid_at = datetime.now(timezone.utc)
                order.status = "paid"
                db.commit()
            else:
                raise HTTPException(status_code=404, detail="Order not found")
        else:
            chinese_model_id_from_request = request.order_data.get('chinese_model_id')
            if chinese_model_id_from_request:
                print(f"✅ Chinese model data available: {chinese_model_id_from_request}")

                brand, model = resolve_phone_model_from_chinese_id(
                    db,
                    chinese_model_id_from_request,
                    device_id
                )

                template = TemplateService.get_template_by_id(db, template_name)
                if not template:
                    print(f"❌ Template '{template_name}' not found in database")
                    raise HTTPException(status_code=400, detail=f"Template '{template_name}' not found in database")

                order_data = {
                    "stripe_session_id": request.session_id,
                    "stripe_payment_intent_id": session.payment_intent,
                    "payment_status": "paid",
                    "paid_at": datetime.now(timezone.utc),
                    "status": "paid",
                    "total_amount": session.amount_total / 100,
                    "currency": session.currency.upper(),
                    "brand_id": brand.id,
                    "model_id": model.id,
                    "template_id": template.id,
                    "user_data": request.order_data
                }
                order = OrderService.create_order(db, order_data)
                print(
                    f"✅ Created order {order.id} with official Chinese brand/model data "
                    f"(brand_id={brand.id}, model_id={model.id})"
                )
            else:
                # Validate that brand, model, and template exist in database (existing logic)
                print(f"🔍 DEBUGGING: Validating brand='{brand_name}', model='{model_name}', template='{template_name}'")
                
                brand = BrandService.get_brand_by_name(db, brand_name)
                if not brand:
                    print(f"❌ Brand '{brand_name}' not found in database")
                    raise HTTPException(status_code=400, detail=f"Brand '{brand_name}' not found in database")
                else:
                    print(f"✅ Brand found: '{brand.name}' (ID: {brand.id})")
                
                model = PhoneModelService.get_model_by_name(db, model_name, brand.id)
                if not model:
                    print(f"❌ Model '{model_name}' not found for brand '{brand_name}' (brand_id: {brand.id})")
                    # Debug: Show available models for this brand
                    available_models = PhoneModelService.get_models_by_brand(db, brand.id, include_unavailable=True)
                    print(f"Available models for brand {brand.name}: {[m.name for m in available_models]}")
                    raise HTTPException(status_code=400, detail=f"Model '{model_name}' not found for brand '{brand_name}'")
                else:
                    print(f"✅ Model found: '{model.name}' (ID: {model.id})")
                
                template = TemplateService.get_template_by_id(db, template_name)
                if not template:
                    print(f"❌ Template '{template_name}' not found in database")
                    raise HTTPException(status_code=400, detail=f"Template '{template_name}' not found in database")
                else:
                    print(f"✅ Template found: '{template.name}' (ID: {template.id})")
                
                # Create new order
                order_data = {
                    "stripe_session_id": request.session_id,
                    "stripe_payment_intent_id": session.payment_intent,
                    "payment_status": "paid",
                    "paid_at": datetime.now(timezone.utc),
                    "status": "paid",
                    "total_amount": session.amount_total / 100,
                    "currency": session.currency.upper(),
                    "brand_id": brand.id,
                    "model_id": model.id,
                    "template_id": template.id,
                    "user_data": request.order_data
                }
                order = OrderService.create_order(db, order_data)
        
        # Complete Chinese API integration for "Pay on App" orders - all 3 endpoints
        chinese_queue_no = None  # Initialize Chinese queue number
        try:
            print(f"=== COMPLETE CHINESE API INTEGRATION START for order {order.id} ===")
            
            # CRITICAL FIX: Retrieve vending session data if device_id is present
            if not device_id:
                device_id = request.order_data.get('device_id')
            vending_session_data = None
            
            # If this is a vending machine payment, retrieve stored session data
            if device_id:
                try:
                    from backend.utils.session_data_manager import SessionDataManager
                    from models import VendingMachineSession
                    
                    print(f"🔍 VENDING PAYMENT DETECTED: Comprehensive session search for device_id {device_id}")
                    
                    # COMPREHENSIVE SESSION SEARCH - try multiple strategies
                    vending_session = None
                    
                    # Strategy 1: Recent sessions with payment-related statuses
                    recent_sessions = db.query(VendingMachineSession).filter(
                        VendingMachineSession.machine_id == device_id,
                        VendingMachineSession.status.in_(["active", "payment_pending", "payment_completed"])
                    ).order_by(VendingMachineSession.created_at.desc()).limit(3).all()
                    
                    print(f"📊 Found {len(recent_sessions)} recent payment-related sessions")
                    for db_session in recent_sessions:
                        print(f"   - Session {db_session.session_id}: status={db_session.status}, created={db_session.created_at}")
                        if db_session.session_data:
                            print(f"     Has session_data with keys: {list(db_session.session_data.keys())}")
                            if 'payment_data' in db_session.session_data:
                                vending_session = db_session
                                print(f"     ✅ FOUND payment_data in session {db_session.session_id}")
                                break
                    
                    # Strategy 2: If no payment data found, try ANY recent session
                    if not vending_session:
                        print(f"🔍 No payment_data found, searching ALL recent sessions for device_id {device_id}")
                        all_sessions = db.query(VendingMachineSession).filter(
                            VendingMachineSession.machine_id == device_id
                        ).order_by(VendingMachineSession.created_at.desc()).limit(5).all()
                        
                        print(f"📊 Found {len(all_sessions)} total sessions:")
                        for db_session in all_sessions:
                            print(f"   - Session {db_session.session_id}: status={db_session.status}, created={db_session.created_at}")
                            if db_session.session_data:
                                print(f"     Session data keys: {list(db_session.session_data.keys())}")
                                # Use the first session with any meaningful data
                                if not vending_session and len(db_session.session_data.keys()) > 2:
                                    vending_session = db_session
                                    print(f"     ✅ Using session {db_session.session_id} as fallback")
                    
                    # Strategy 3: Try to find by third_id from previous logs (if available)
                    if not vending_session:
                        print(f"🔍 Strategy 3: Checking recent sessions with chinese_third_id")
                        sessions_with_chinese_data = db.query(VendingMachineSession).filter(
                            VendingMachineSession.machine_id == device_id
                        ).order_by(VendingMachineSession.created_at.desc()).limit(10).all()
                        
                        for db_session in sessions_with_chinese_data:
                            if db_session.session_data and 'chinese_third_id' in db_session.session_data:
                                vending_session = db_session
                                print(f"     ✅ Found session with chinese_third_id: {db_session.session_id}")
                                break
                    
                    # Strategy 4: Last resort - use SessionDataManager's find_session_by_third_id
                    if not vending_session:
                        print(f"🔍 Strategy 4: Last resort - checking payment mappings for device {device_id}")
                        # Try to find any recent third_id from logs or payment mappings
                        try:
                            # Check if there are any PaymentMapping entries for this device
                            from models import PaymentMapping
                            recent_payments = db.query(PaymentMapping).filter(
                                PaymentMapping.device_id == device_id
                            ).order_by(PaymentMapping.created_at.desc()).limit(3).all()
                            
                            for payment in recent_payments:
                                print(f"     Checking payment mapping third_id: {payment.third_id}")
                                found_session = SessionDataManager.find_session_by_third_id(db, payment.third_id)
                                if found_session and found_session.machine_id == device_id:
                                    vending_session = found_session
                                    print(f"     ✅ Found session via PaymentMapping: {found_session.session_id}")
                                    break
                        except Exception as mapping_error:
                            print(f"     PaymentMapping lookup failed: {mapping_error}")
                    
                    # Extract data if session found
                    if vending_session and vending_session.session_data:
                        vending_session_data = vending_session.session_data
                        print(f"✅ FINAL: Using vending session {vending_session.session_id}")
                        print(f"📊 Session status: {vending_session.status}")
                        print(f"📊 Session data keys: {list(vending_session_data.keys())}")
                        
                        # Extract payment data using SessionDataManager
                        payment_data = SessionDataManager.get_session_payment_data(vending_session)
                        if payment_data:
                            print(f"✅ Extracted payment data keys: {list(payment_data.keys())}")
                            for key, value in payment_data.items():
                                print(f"     - {key}: {value}")
                        else:
                            print(f"⚠️ No payment_data found in session, checking raw session_data")
                            # Fallback: check for chinese_third_id and other data directly
                            if 'chinese_third_id' in vending_session_data:
                                print(f"     Found chinese_third_id: {vending_session_data['chinese_third_id']}")
                            if 'order_summary' in vending_session_data:
                                order_summary = vending_session_data['order_summary']
                                print(f"     Found order_summary with keys: {list(order_summary.keys())}")
                    else:
                        print(f"❌ CRITICAL: NO VENDING SESSION DATA FOUND for device_id {device_id}")
                        print(f"❌ This means payment initialization may have failed or session was lost")
                        
                        # FINAL DEBUGGING: List ALL sessions for this device to understand what happened
                        try:
                            print(f"🔍 FINAL DEBUG: Listing ALL sessions for device {device_id}:")
                            debug_sessions = db.query(VendingMachineSession).filter(
                                VendingMachineSession.machine_id == device_id
                            ).order_by(VendingMachineSession.created_at.desc()).limit(10).all()
                            
                            if debug_sessions:
                                for i, db_session in enumerate(debug_sessions):
                                    print(f"   {i+1}. {db_session.session_id}")
                                    print(f"      Status: {db_session.status}")
                                    print(f"      Created: {db_session.created_at}")
                                    print(f"      Has session_data: {db_session.session_data is not None}")
                                    if db_session.session_data:
                                        print(f"      Session data size: {len(str(db_session.session_data))} chars")
                                        print(f"      Session data keys: {list(db_session.session_data.keys())}")
                                        # Show first few chars of each value for debugging
                                        for key, value in db_session.session_data.items():
                                            if isinstance(value, dict):
                                                print(f"        {key}: {{{', '.join(value.keys())}}}")
                                            else:
                                                value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                                                print(f"        {key}: {value_str}")
                            else:
                                print(f"   NO SESSIONS FOUND AT ALL for device_id {device_id}")
                        except Exception as debug_error:
                            print(f"   Debug session listing failed: {debug_error}")
                        
                        vending_session_data = None
                        
                except Exception as session_error:
                    print(f"❌ CRITICAL ERROR in session retrieval: {str(session_error)}")
                    import traceback
                    print(f"❌ Traceback: {traceback.format_exc()}")
                    vending_session_data = None
            
            # Get Chinese model ID from multiple sources (priority order)
            chinese_model_id = None
            mobile_shell_id = None
            stored_third_id = None
            
            # Priority 1: Vending session data (comprehensive extraction)
            if vending_session_data:
                print(f"🔍 EXTRACTING DATA from vending session...")
                
                # Method 1: Extract from payment_data structure
                if 'payment_data' in vending_session_data:
                    payment_data = vending_session_data['payment_data']
                    chinese_model_id = payment_data.get('mobile_model_id')
                    mobile_shell_id = payment_data.get('mobile_shell_id')
                    stored_third_id = payment_data.get('third_id')
                    print(f"✅ Extracted from payment_data structure")
                
                # Method 2: Extract from order_summary if payment_data not available
                if not chinese_model_id and 'order_summary' in vending_session_data:
                    order_summary = vending_session_data['order_summary']
                    chinese_model_id = order_summary.get('chinese_model_id')
                    mobile_shell_id = order_summary.get('mobile_shell_id')
                    print(f"📋 Extracted from order_summary: chinese_model_id={chinese_model_id}")
                
                # Method 3: Extract from root level (legacy compatibility)
                if not stored_third_id:
                    stored_third_id = vending_session_data.get('chinese_third_id')
                    print(f"🔧 Found stored_third_id at root level: {stored_third_id}")
                
                # Method 4: Try to get device_id from session if not from request
                session_device_id = vending_session_data.get('device_id') or vending_session_data.get('machine_id')
                if session_device_id and session_device_id != device_id:
                    print(f"⚠️ Device ID mismatch: request={device_id}, session={session_device_id}")
                
                print(f"✅ FINAL EXTRACTED DATA from vending session:")
                print(f"   - chinese_model_id: {chinese_model_id}")
                print(f"   - mobile_shell_id: {mobile_shell_id}")
                print(f"   - stored_third_id: {stored_third_id}")
                print(f"   - session_device_id: {session_device_id}")
            
            # Priority 2: Request order data  
            if not chinese_model_id:
                chinese_model_id = request.order_data.get('chinese_model_id')
                print(f"📝 Using chinese_model_id from request: {chinese_model_id}")
            
            # Priority 3: Database model lookup (only if model object exists from validation)
            if not chinese_model_id and 'model' in locals():
                chinese_model_id = model.chinese_model_id
                print(f"🗄️ Using chinese_model_id from database: {chinese_model_id}")
            
            # Get mobile_shell_id from multiple sources if not from vending session
            if not mobile_shell_id:
                mobile_shell_id = (
                    request.order_data.get('mobile_shell_id') or 
                    request.order_data.get('selectedModelData', {}).get('mobile_shell_id')
                )
                print(f"📝 Using mobile_shell_id from request: {mobile_shell_id}")
            
            # Get stored third_id from multiple sources if not from vending session
            if not stored_third_id:
                stored_third_id = request.order_data.get('paymentThirdId') or request.order_data.get('third_id')
                print(f"📝 Using stored_third_id from request: {stored_third_id}")
            
            print(f"🎯 FINAL RESOLVED DATA:")
            print(f"   - device_id: {device_id}")
            print(f"   - chinese_model_id: {chinese_model_id}")
            print(f"   - mobile_shell_id: {mobile_shell_id}")
            print(f"   - stored_third_id: {stored_third_id}")
            
            # CRITICAL: Enhanced validation layers for vending payments
            if device_id:  # This is a vending payment
                validation_errors = []
                
                if not chinese_model_id:
                    validation_errors.append("chinese_model_id is missing")
                if not mobile_shell_id:
                    validation_errors.append("mobile_shell_id is missing")
                
                if validation_errors:
                    print(f"❌ CRITICAL VALIDATION FAILED for vending payment:")
                    for error in validation_errors:
                        print(f"   - {error}")
                    
                    print(f"📊 Data availability analysis:")
                    print(f"   - vending_session_data available: {vending_session_data is not None}")
                    print(f"   - vending_session_data keys: {list(vending_session_data.keys()) if vending_session_data else 'N/A'}")
                    print(f"   - payment_data available: {'payment_data' in (vending_session_data or {})}")
                    print(f"   - request.order_data keys: {list(request.order_data.keys())}")
                    
                    # Provide detailed error with recovery suggestions
                    error_detail = f"Vending machine payment validation failed: {', '.join(validation_errors)}. "
                    if not vending_session_data:
                        error_detail += "No vending session data found. Please restart the vending machine flow."
                    elif 'payment_data' not in vending_session_data:
                        error_detail += "Payment initialization data missing. Please try the payment again."
                    else:
                        error_detail += "Required model information missing. Please select your phone model again."
                    
                    raise HTTPException(status_code=400, detail=error_detail)
                else:
                    print(f"✅ Vending payment validation PASSED - all required fields present")
            
            # Determine if this is a vending machine payment based on payment method or presence of device_id
            payment_method = request.order_data.get('paymentMethod', 'app')
            is_vending_payment = payment_method == 'vending_machine' or bool(device_id)
            
            print(f"Payment method: {payment_method}, has device_id: {bool(device_id)}, is_vending_payment: {is_vending_payment}")
            
            if not device_id and is_vending_payment:
                raise HTTPException(status_code=400, detail="device_id is required for vending machine payments")
            elif not device_id:
                print(f"⚠️ No device_id provided - skipping Chinese API integration (app-only payment)")
                chinese_queue_no = None
                # Skip Chinese API integration for app-only payments without device_id
                print(f"=== COMPLETE CHINESE API INTEGRATION END (SKIPPED - NO DEVICE_ID) ===")
            else:
                # CRITICAL FIX: Use resolved stored payment data
                existing_third_id = stored_third_id
                existing_chinese_payment_id = request.order_data.get('chinesePaymentId') or request.order_data.get('chinese_payment_id')
                
                # Extract Chinese payment ID from vending session data if available
                if not existing_chinese_payment_id and vending_session_data:
                    existing_chinese_payment_id = vending_session_data.get('chinese_payment_id')
                
                print(f"Payment data validation:")
                print(f"  - existing_third_id: {existing_third_id}")
                print(f"  - existing_chinese_payment_id: {existing_chinese_payment_id}")
                print(f"  - device_id: {device_id}")
                print(f"  - chinese_model_id: {chinese_model_id}")
                
                # Enhanced validation for vending payments
                if is_vending_payment and device_id and not existing_third_id:
                    if vending_session_data:
                        print(f"⚠️ WARNING: Vending payment found session data but missing third_id - will generate new one")
                    else:
                        print(f"❌ CRITICAL: Vending payment missing stored payment data - this will cause duplicate payData")
                        print(f"Available order_data keys: {list(request.order_data.keys())}")
                        # Don't fail here, but log warning - the duplicate call will still work
                
                if chinese_model_id:
                    # Generate third_id for Chinese API if not provided from frontend
                    from backend.utils.helpers import generate_third_id
                    third_id = existing_third_id or generate_third_id()
                    
                    print(f"Chinese API integration: device_id={device_id}, model_id={chinese_model_id}, third_id={third_id}")
                    
                    # Import Chinese API functions
                    from backend.services.chinese_payment_service import (
                        send_payment_to_chinese_api, 
                        send_payment_status_to_chinese_api,
                        send_order_data_to_chinese_api
                    )
                
                    # STEP 1: Send payment data to Chinese API (if not already done by frontend)
                    print(f"STEP 1: Sending payment data to Chinese API...")
                    chinese_payment_response = None
                    
                    if not existing_third_id:
                        # Frontend didn't call payData, so we need to call it now
                        print(f"⚠️ WARNING: No stored payment data found - making new payData call (potential duplicate)")
                        chinese_payment_response = send_payment_to_chinese_api(
                            mobile_model_id=chinese_model_id,
                            device_id=device_id,
                            third_id=third_id,
                            pay_amount=float(session.amount_total / 100),
                            pay_type=12  # App payment type
                        )
                        print(f"Chinese API payData response: {chinese_payment_response}")
                    else:
                        print(f"✅ Payment data already sent by frontend with third_id: {third_id}")
                        # Create a mock response using stored data
                        chinese_payment_response = {
                            'code': 200,
                            'data': {'id': existing_chinese_payment_id or 'FRONTEND_SENT'},
                            'msg': 'Using stored frontend payment data (duplicate call avoided)'
                        }
                    
                    # STEP 2: Send payment status notification (NEW)
                    print(f"STEP 2: Sending payment status notification to Chinese API...")
                    try:
                        payment_status_response = send_payment_status_to_chinese_api(
                            third_id=third_id,
                            status=3,  # 3 = Paid status in Chinese system
                            pay_amount=float(session.amount_total / 100)
                        )
                        print(f"Chinese API payStatus response: {payment_status_response}")
                        
                        if payment_status_response.get('code') == 200:
                            print("SUCCESS: Payment status notification sent to Chinese API")
                        else:
                            print(f"WARNING: Payment status notification failed: {payment_status_response.get('msg')}")
                            
                    except Exception as status_error:
                        print(f"WARNING: Payment status notification failed: {str(status_error)}")
                        # Continue with order data submission even if status notification fails
                    
                    # STEP 3: Generate design image URL with secure token and send order data
                    print(f"STEP 3: Preparing order data for Chinese API...")
                    
                    try:
                        from backend.services.file_service import generate_partner_specific_token
                        
                        # Get final design image URL for Chinese API
                        base_image_url = None
                        filename = None
                        
                        # Priority 1: Use the uploaded final image URL (permanent, hosted on render.com)
                        if request.order_data.get('finalImagePublicUrl'):
                            base_image_url = request.order_data.get('finalImagePublicUrl')
                            # Extract filename from URL for token generation
                            filename = base_image_url.split('/image/')[-1] if '/image/' in base_image_url else None
                            print(f"✅ Using uploaded final image URL: {base_image_url}")
                            
                        # Priority 2: Try to find session-based filename if we have session ID
                        elif request.order_data.get('imageSessionId'):
                            session_id = request.order_data.get('imageSessionId')
                            # Try to construct filename based on session ID (this is a fallback)
                            filename = f"order-{session_id}-final-*.png"
                            base_image_url = f"https://pimpmycase.onrender.com/image/{filename}"
                            print(f"⚠️ Using session-based URL pattern: {base_image_url}")
                            
                        # Priority 3: Check if designImage is already a permanent URL
                        elif request.order_data.get('designImage') and request.order_data.get('designImage').startswith('https://pimpmycase.onrender.com'):
                            base_image_url = request.order_data.get('designImage')
                            # CRITICAL FIX: Extract CLEAN filename, removing ALL existing token parameters
                            filename = base_image_url.split('/image/')[-1].split('?')[0] if '/image/' in base_image_url else None
                            print(f"✅ Using existing permanent URL from designImage: {base_image_url}")
                            print(f"🔧 Extracted clean filename: {filename}")
                            
                        # Priority 4: Check if pic field contains permanent URL  
                        elif request.order_data.get('pic') and request.order_data.get('pic').startswith('https://pimpmycase.onrender.com'):
                            base_image_url = request.order_data.get('pic')
                            # CRITICAL FIX: Extract CLEAN filename, removing ALL existing token parameters
                            filename = base_image_url.split('/image/')[-1].split('?')[0] if '/image/' in base_image_url else None
                            print(f"✅ Using existing permanent URL from pic field: {base_image_url}")
                            print(f"🔧 Extracted clean filename: {filename}")
                            
                        # NO FALLBACK - User specifically requested no fallback handling
                        else:
                            print(f"❌ CRITICAL: No valid image URL found in order data")
                            print(f"Available order_data keys: {list(request.order_data.keys())}")
                            print(f"finalImagePublicUrl: {request.order_data.get('finalImagePublicUrl')}")
                            print(f"designImage: {request.order_data.get('designImage')}")
                            print(f"imageSessionId: {request.order_data.get('imageSessionId')}")
                            raise HTTPException(status_code=400, detail="No valid image URL provided - cannot proceed with Chinese API order")
                        
                        # Generate secure token for Chinese API access (48 hours expiry)
                        if filename and base_image_url.startswith('https://pimpmycase.onrender.com/image/'):
                            try:
                                print(f"🔧 CRITICAL FIX: Generating NEW secure URL with CLEAN filename")
                                print(f"   Clean filename: {filename}")
                                print(f"   Original URL had tokens: {'?' in base_image_url}")
                                
                                # Generate Chinese manufacturing partner token with 48-hour expiry
                                secure_token = generate_partner_specific_token(
                                    filename, 
                                    partner_type="chinese_manufacturing", 
                                    custom_expiry_hours=48
                                )
                                
                                # CRITICAL FIX: Build NEW clean URL using ONLY the filename and new token
                                design_image_url = f"https://pimpmycase.onrender.com/image/{filename}?token={secure_token}"
                                
                                # Validate no duplicate tokens
                                token_count = design_image_url.count('?token=')
                                if token_count != 1:
                                    raise ValueError(f"Generated URL has {token_count} token parameters - should have exactly 1")
                                
                                print(f"✅ Generated CLEAN secure Chinese manufacturing token (48h)")
                                print(f"   Original URL: {base_image_url}")
                                print(f"   New Clean URL: {design_image_url}")
                                print(f"   Token count: {token_count} (correct)")
                                
                            except Exception as token_error:
                                print(f"❌ Chinese manufacturing token generation failed: {token_error}")
                                print(f"⚠️ Falling back to base URL - this may cause Chinese API authentication failures")
                                design_image_url = base_image_url
                        else:
                            design_image_url = base_image_url
                            print(f"ℹ️ Using base URL (no Chinese manufacturing token needed): {design_image_url}")
                        
                        # Generate order third_id (different from payment third_id) 
                        # Use session ID as base if available for consistency
                        order_prefix = "OREN"
                        if request.order_data.get('imageSessionId'):
                            order_third_id = f"{order_prefix}-{request.order_data.get('imageSessionId')}"
                        else:
                            order_third_id = generate_third_id("OREN")
                        
                        # CRITICAL FIX: Always use our original third_id (PYEN...) for third_pay_id
                        # The Chinese API keys payment records by the third_id we sent in payData, not their internal id
                        effective_third_pay_id = third_id  # Always use our original PYEN... ID
                        
                        print(f"✅ Using original third_id for orderData third_pay_id: {effective_third_pay_id}")
                        
                        # Log for debugging - we can still track the Chinese internal ID separately
                        from backend.routes.chinese_api import get_payment_mapping
                        chinese_internal_id = get_payment_mapping(db, third_id) if third_id.startswith('PYEN') else None
                        if chinese_internal_id:
                            print(f"ℹ️ Chinese internal payment ID (for reference): {chinese_internal_id}")
                        else:
                            print(f"ℹ️ No Chinese internal payment ID found (this is OK for orderData)")
                        
                        # CRITICAL FIX: Extract mobile_shell_id from multiple sources with validation
                        print(f"DEBUG: Full order_data received: {request.order_data}")
                        
                        # CRITICAL FIX: Use mobile_shell_id already resolved from vending session or fallback to database
                        if not mobile_shell_id and chinese_model_id:
                            try:
                                # Try to find mobile_shell_id from phone model database
                                phone_model = db.query(PhoneModel).filter(
                                    PhoneModel.chinese_model_id == chinese_model_id
                                ).first()
                                
                                if phone_model and hasattr(phone_model, 'mobile_shell_id'):
                                    mobile_shell_id = phone_model.mobile_shell_id
                                    print(f"✅ Mobile shell ID retrieved from database: {mobile_shell_id}")
                            except Exception as db_error:
                                print(f"⚠️ Database lookup for mobile_shell_id failed: {db_error}")
                        
                        if not mobile_shell_id:
                            print(f"❌ CRITICAL: mobile_shell_id not found - this WILL cause orderData to fail")
                            print(f"Sources checked: vending_session_data, request.order_data, database")
                            
                            # CRITICAL FIX: Fail the vending machine payment if mobile_shell_id is missing
                            if is_vending_payment and device_id:
                                raise HTTPException(
                                    status_code=400,
                                    detail="Vending machine payment failed: mobile_shell_id is required for Chinese API integration. Please select your phone model again."
                                )
                            else:
                                # For app-only payments, still try to proceed but log warning
                                print(f"⚠️ App payment proceeding without mobile_shell_id - Chinese API may fail")
                                mobile_shell_id = None
                        else:
                            print(f"✅ Mobile shell ID resolved: {mobile_shell_id}")
                        
                        print(f"Sending order data: third_pay_id={effective_third_pay_id} (Chinese ID), third_id={order_third_id}")
                        print(f"Original payment ID: {third_id}")
                        print(f"Design image URL: {design_image_url}")
                        print(f"Mobile shell ID: {mobile_shell_id}")
                        
                        # Always call orderData if we have device_id - let Chinese API handle validation
                        print(f"✅ Calling Chinese API orderData")
                        order_data_response = send_order_data_to_chinese_api(
                            third_pay_id=effective_third_pay_id,  # Use Chinese payment ID (MSPY...)
                            third_id=order_third_id,  # Order ID 
                            mobile_model_id=chinese_model_id,
                            pic=design_image_url,
                            device_id=device_id,
                            mobile_shell_id=mobile_shell_id
                        )
                        
                        print(f"Chinese API orderData response: {order_data_response}")
                        
                        if order_data_response.get('code') == 200:
                            print("SUCCESS: Order data sent to Chinese API for printing")
                            order_data = order_data_response.get('data', {})
                            
                            # Store Chinese order information
                            order.chinese_order_id = order_data.get('id')
                            order.queue_number = order_data.get('queue_no')
                            order.chinese_order_status = order_data.get('status', 8)  # 8 = Waiting for printing
                            
                            # Use Chinese API queue number if available
                            chinese_queue_no = order_data.get('queue_no')
                            if chinese_queue_no:
                                print(f"✅ Using Chinese API queue number: {chinese_queue_no}")
                            
                        else:
                            print(f"WARNING: Order data submission failed: {order_data_response.get('msg')}")
                            chinese_queue_no = None
                            
                    except Exception as order_error:
                        print(f"WARNING: Order data submission failed: {str(order_error)}")
                        import traceback
                        traceback.print_exc()
                        chinese_queue_no = None
                    
                    # Store Chinese payment info in order (from step 1)
                    if chinese_payment_response and chinese_payment_response.get('code') == 200:
                        order.third_party_payment_id = third_id
                        order.chinese_payment_id = chinese_payment_response.get('data', {}).get('id')
                        order.chinese_payment_status = 3  # Paid status in Chinese system
                        db.commit()
                        print(f"Successfully completed Chinese API integration")
                    else:
                        print(f"Chinese API payment failed: {chinese_payment_response.get('msg') if chinese_payment_response else 'No response'}")
                        chinese_queue_no = None
                        
                # No Chinese model ID found
                else:
                    if is_vending_payment and device_id:
                        print(f"❌ CRITICAL: Vending payment has device_id but missing chinese_model_id - Chinese API integration required")
                        print(f"This is likely due to model selection not being persisted properly")
                        # For vending payments, Chinese model ID is mandatory
                        raise HTTPException(
                            status_code=400, 
                            detail="Chinese model ID missing for vending payment - please select your phone model again"
                        )
                    else:
                        print(f"ℹ️ App payment without Chinese model ID - skipping Chinese API integration")
                        chinese_queue_no = None
                    
            print(f"=== COMPLETE CHINESE API INTEGRATION END ===")
                
        except Exception as chinese_error:
            print(f"CRITICAL: Chinese API integration failed: {str(chinese_error)}")
            import traceback
            traceback.print_exc()
            chinese_queue_no = None
            # Don't fail the order if Chinese API fails, just log the error
        
        # CRITICAL FIX: Only use Chinese API queue numbers - no fallback generation
        if chinese_queue_no:
            queue_no = chinese_queue_no
            print(f"✅ Final queue number from Chinese API: {queue_no}")
            
            return {
                "success": True,
                "order_id": order.id,
                "payment_id": session.payment_intent,
                "queue_no": queue_no,
                "status": "paid",
                "brand": brand_name,
                "model": model_name,
                "color": color,
                "template_id": template_name,
                "amount": session.amount_total / 100
            }
        else:
            # No fallback queue number - Chinese API integration is mandatory for vending payments
            print(f"❌ CRITICAL: Chinese API integration failed - cannot generate queue number without Chinese approval")
            
            if is_vending_payment and device_id:
                # For vending machine payments, Chinese API is mandatory
                raise HTTPException(
                    status_code=503,
                    detail="Vending machine payment failed: Chinese API integration required but unavailable. Please try again or contact support."
                )
            else:
                # For app-only payments without device_id, return success without queue number
                print(f"ℹ️ App-only payment completed without vending machine integration")
                return {
                    "success": True,
                    "order_id": order.id,
                    "payment_id": session.payment_intent,
                    "queue_no": None,  # No queue number for app-only payments
                    "status": "paid",
                    "brand": brand_name,
                    "model": model_name,
                    "color": color,
                    "template_id": template_name,
                    "amount": session.amount_total / 100,
                    "note": "App payment completed - no vending machine queue"
                }
        
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        print(f"Payment processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")

@router.post("/stripe-webhook")
async def stripe_webhook_handler(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
            )
        except ValueError:
            # Invalid payload
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            raise HTTPException(status_code=400, detail="Invalid signature")

        print(f"Stripe webhook received: {event['type']}")
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            print(f"Payment successful for session: {session['id']}")
            
            # You can process the payment here if needed
            # For now, just log and return success
            
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            print(f"Payment intent succeeded: {payment_intent['id']}")
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            print(f"Payment failed: {payment_intent['id']}")
            
        else:
            print(f"Unhandled event type: {event['type']}")

        return {"success": True, "event_type": event['type']}

    except HTTPException:
        # Re-raise HTTPException as-is (preserves status codes like 400)
        raise
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")
