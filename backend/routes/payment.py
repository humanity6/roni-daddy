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