"""Payment processing API routes - Stripe integration"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from backend.schemas.payment import CheckoutSessionRequest, PaymentSuccessRequest
from backend.services.payment_service import initialize_stripe
from db_services import OrderService, BrandService, PhoneModelService, TemplateService
from datetime import datetime, timezone
import stripe
import os
import time

router = APIRouter()

# Stripe is initialized in the payment service
stripe_client = initialize_stripe()

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db)
):
    """Create a Stripe Checkout session"""
    try:
        # Convert amount to pence (Stripe requires integers)
        amount_pence = int(request.amount * 100)
        
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
        
        # Handle test sessions differently
        if session_id.startswith('cs_test_session'):
            # Mock payment success for test sessions
            session = type('MockSession', (), {
                'payment_status': 'paid',
                'metadata': {'template_id': 'classic', 'brand': 'iPhone', 'model': 'iPhone 14'},
                'created': int(time.time()),
                'payment_intent': 'pi_test_12345',
                'amount_total': 1998,  # Mock amount in pence (£19.98)
                'currency': 'gbp'
            })()
            print(f"Test session - mocking successful payment")
        else:
            # Retrieve checkout session to verify payment
            session = stripe.checkout.Session.retrieve(session_id)
            print(f"Checkout session status: {session.payment_status}")
            
            if session.payment_status != 'paid':
                raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Get metadata from session
        template_name = session.metadata.get('template_id', 'classic')
        brand_name = session.metadata.get('brand', 'iPhone')
        model_name = session.metadata.get('model', 'iPhone 15 Pro')
        color = session.metadata.get('color', 'Natural Titanium')
        
        # Generate queue number for display
        queue_no = f"Q{str(int(session.created))[-6:]}"
        
        return {
            "success": True,
            "session_id": session_id,
            "payment_id": session.payment_intent,
            "queue_no": queue_no,
            "status": "paid",
            "brand": brand_name,
            "model": model_name,
            "color": color,
            "template_id": template_name,
            "amount": session.amount_total / 100
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
        
        # Handle test sessions differently
        if request.session_id.startswith('cs_test_session'):
            # Mock payment success for test sessions
            session = type('MockSession', (), {
                'payment_status': 'paid',
                'metadata': {'template_id': 'classic', 'brand': 'iPhone', 'model': 'iPhone 14'},
                'created': int(time.time()),
                'payment_intent': 'pi_test_12345',
                'amount_total': 1998,  # Mock amount in pence (£19.98)
                'currency': 'gbp'
            })()
            print(f"Test session - mocking successful payment processing")
        else:
            # Retrieve checkout session to verify payment
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
            # Validate that brand, model, and template exist in database
            brand = BrandService.get_brand_by_name(db, brand_name)
            if not brand:
                raise HTTPException(status_code=400, detail=f"Brand '{brand_name}' not found in database")
            
            model = PhoneModelService.get_model_by_name(db, model_name, brand.id)
            if not model:
                raise HTTPException(status_code=400, detail=f"Model '{model_name}' not found for brand '{brand_name}'")
            
            template = TemplateService.get_template_by_id(db, template_name)
            if not template:
                raise HTTPException(status_code=400, detail=f"Template '{template_name}' not found in database")
            
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
        try:
            print(f"=== COMPLETE CHINESE API INTEGRATION START for order {order.id} ===")
            
            # Get Chinese model ID from order data or device_id from request
            device_id = request.order_data.get('device_id')
            if not device_id:
                raise HTTPException(status_code=400, detail="device_id is required for Chinese API integration")
            chinese_model_id = request.order_data.get('chinese_model_id') or model.chinese_model_id
            
            # Get third_id from request data if available (from PaymentScreen.jsx)
            existing_third_id = request.order_data.get('paymentThirdId') or request.order_data.get('third_id')
            
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
                    chinese_payment_response = send_payment_to_chinese_api(
                        mobile_model_id=chinese_model_id,
                        device_id=device_id,
                        third_id=third_id,
                        pay_amount=float(session.amount_total / 100),
                        pay_type=12  # App payment type
                    )
                    print(f"Chinese API payData response: {chinese_payment_response}")
                else:
                    print(f"Payment data already sent by frontend with third_id: {third_id}")
                    # Create a mock response for consistency
                    chinese_payment_response = {
                        'code': 200,
                        'data': {'id': request.order_data.get('chinesePaymentId') or request.order_data.get('chinese_payment_id', 'FRONTEND_SENT')}
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
                        # Extract filename from URL for token generation
                        filename = base_image_url.split('/image/')[-1] if '/image/' in base_image_url else None
                        print(f"✅ Using existing permanent URL: {base_image_url}")
                        
                    # Priority 4: Fallback for blob URLs or missing images
                    else:
                        print(f"⚠️ No permanent image URL found, using fallback")
                        base_image_url = f"https://pimpmycase.onrender.com/api/generate-design-preview"
                        filename = None  # No token needed for fallback URL
                    
                    # Generate secure token for Chinese API access (48 hours expiry)
                    if filename and base_image_url.startswith('https://pimpmycase.onrender.com/image/'):
                        try:
                            # Generate Chinese manufacturing partner token with 48-hour expiry
                            secure_token = generate_partner_specific_token(
                                filename, 
                                partner_type="chinese_manufacturing", 
                                custom_expiry_hours=48
                            )
                            design_image_url = f"{base_image_url}?token={secure_token}"
                            print(f"🔐 Generated secure Chinese manufacturing token (48h) for: {design_image_url}")
                        except Exception as token_error:
                            print(f"⚠️ Chinese manufacturing token generation failed: {token_error}, using base URL")
                            design_image_url = base_image_url
                    else:
                        design_image_url = base_image_url
                        print(f"ℹ️ Using base URL (no token needed): {design_image_url}")
                    
                    # Generate order third_id (different from payment third_id) 
                    # Use session ID as base if available for consistency
                    order_prefix = "OREN"
                    if request.order_data.get('imageSessionId'):
                        order_third_id = f"{order_prefix}-{request.order_data.get('imageSessionId')}"
                    else:
                        order_third_id = generate_third_id("OREN")
                    
                    # Get Chinese payment ID from database mapping (MSPY...) instead of using PYEN...
                    from backend.routes.chinese_api import get_payment_mapping
                    chinese_payment_id = None
                    
                    if third_id.startswith('PYEN'):
                        chinese_payment_id = get_payment_mapping(db, third_id)
                        if not chinese_payment_id:
                            print(f"⚠️ WARNING: No Chinese payment ID found for {third_id} - this may cause orderData to fail")
                    
                    # Use Chinese payment ID (MSPY...) for third_pay_id if available, otherwise use original
                    effective_third_pay_id = chinese_payment_id if chinese_payment_id else third_id
                    
                    # Extract mobile_shell_id from order data (set by model selection screens)
                    print(f"DEBUG: Full order_data received: {request.order_data}")
                    mobile_shell_id = request.order_data.get('mobile_shell_id')
                    if not mobile_shell_id:
                        print(f"⚠️ WARNING: mobile_shell_id not found in order data - this may cause orderData to fail")
                        print(f"Available keys in order_data: {list(request.order_data.keys())}")
                    else:
                        print(f"✅ Mobile shell ID extracted: {mobile_shell_id}")
                    
                    print(f"Sending order data: third_pay_id={effective_third_pay_id} (Chinese ID), third_id={order_third_id}")
                    print(f"Original payment ID: {third_id}")
                    print(f"Design image URL: {design_image_url}")
                    
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
                        
                    else:
                        print(f"WARNING: Order data submission failed: {order_data_response.get('msg')}")
                        
                except Exception as order_error:
                    print(f"WARNING: Order data submission failed: {str(order_error)}")
                    import traceback
                    traceback.print_exc()
                
                # Store Chinese payment info in order (from step 1)
                if chinese_payment_response and chinese_payment_response.get('code') == 200:
                    order.third_party_payment_id = third_id
                    order.chinese_payment_id = chinese_payment_response.get('data', {}).get('id')
                    order.chinese_payment_status = 3  # Paid status in Chinese system
                    db.commit()
                    print(f"Successfully completed Chinese API integration")
                else:
                    print(f"Chinese API payment failed: {chinese_payment_response.get('msg') if chinese_payment_response else 'No response'}")
                    
                print(f"=== COMPLETE CHINESE API INTEGRATION END ===")
                
            else:
                print(f"No Chinese model ID found for app payment, skipping Chinese API integration")
                
        except Exception as chinese_error:
            print(f"CRITICAL: Chinese API integration failed: {str(chinese_error)}")
            import traceback
            traceback.print_exc()
            # Don't fail the order if Chinese API fails, just log the error
        
        # Generate queue number for display
        queue_no = f"Q{str(order.created_at.timestamp())[-6:]}"
        
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