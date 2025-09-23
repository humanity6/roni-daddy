"""Chinese API Mock Server
Mimics the Chinese manufacturer API for local development
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
import asyncio
import threading
import logging

import requests
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chinese API Mock", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
current_dir = os.path.dirname(__file__)
fixtures_dir = os.path.join(current_dir, "fixtures")

# In-memory storage for tokens and payment status
mock_tokens = {}
payment_statuses = {}  # third_id -> status
order_statuses = {}    # third_id -> status

def load_fixture(filename: str) -> Dict[str, Any]:
    """Load JSON fixture from fixtures directory"""
    filepath = os.path.join(fixtures_dir, filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Fixture file not found: {filepath}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in fixture file: {filepath}")
        return {}

def mock_response(data: Any, code: int = 200, msg: str = "Success") -> Dict[str, Any]:
    """Create standardized mock response"""
    return {
        "code": code,
        "msg": msg,
        "data": data
    }

def generate_mock_token() -> str:
    """Generate a mock authentication token"""
    timestamp = str(int(time.time()))
    return f"mock_token_{timestamp}"

def validate_signature(request_data: Dict[str, Any], signature: str) -> bool:
    """Mock signature validation - always returns True for development"""
    return True

def send_webhook_async(url: str, payload: Dict[str, Any], delay: float = 0):
    """Send webhook asynchronously with optional delay"""
    def _send():
        if delay > 0:
            time.sleep(delay)
        try:
            response = requests.post(url, json=payload, timeout=10)
            logger.info(f"Webhook sent to {url}: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send webhook to {url}: {e}")

    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/mobileShell/en/device/generateQR")
async def generate_qr_code(request: Request):
    """Mock QR code generation endpoint - simulates vending machine QR generation"""
    logger.info("Mock QR code generation request received")

    body = await request.json()
    machine_id = body.get("machine_id", "MOCK_MACHINE_001")

    # Use predefined device IDs that have models in fixtures
    available_devices = ["TEST_DEVICE_001", "TEST_DEVICE_002"]
    device_id = available_devices[int(time.time()) % len(available_devices)]

    # Generate QR code URL that points to frontend with device_id
    qr_url = f"http://localhost:5173/?device_id={device_id}&machine_id={machine_id}"

    response_data = {
        "device_id": device_id,
        "machine_id": machine_id,
        "qr_url": qr_url,
        "qr_data": qr_url,  # The actual data in the QR code
        "expires_at": int(time.time()) + 1800,  # 30 minutes from now
        "status": "active"
    }

    logger.info(f"Generated QR code for device: {device_id}")
    return mock_response(response_data)

@app.get("/qr/{device_id}")
async def get_qr_redirect(device_id: str):
    """Mock QR code redirect endpoint - simulates scanning QR code"""
    logger.info(f"QR code scanned for device: {device_id}")

    # Redirect to frontend with device_id
    from fastapi.responses import RedirectResponse
    redirect_url = f"http://localhost:5173/?device_id={device_id}&source=qr_scan"

    return RedirectResponse(url=redirect_url, status_code=302)

@app.post("/mobileShell/en/user/login")
async def login(request: Request):
    """Mock login endpoint"""
    logger.info("Mock login request received")

    body = await request.json()
    account = body.get("account")
    password = body.get("password")

    login_data = load_fixture("login.json")

    # Generate mock token
    token = generate_mock_token()
    mock_tokens[token] = {
        "account": account,
        "created_at": time.time()
    }

    # Return login response with token
    response_data = login_data.get("success_response", {})
    if response_data.get("data"):
        response_data["data"]["token"] = token

    logger.info(f"Mock login successful for account: {account}")
    return mock_response(response_data.get("data", {"token": token}))

@app.post("/mobileShell/en/brand/list")
async def get_brands(request: Request, authorization: str = Header(None)):
    """Mock brands list endpoint"""
    logger.info("Mock brands request received")

    brands_data = load_fixture("brands.json")
    return mock_response(brands_data.get("data", []))

@app.post("/mobileShell/en/stock/list")
async def get_stock_models(request: Request, authorization: str = Header(None)):
    """Mock stock models endpoint"""
    logger.info("Mock stock models request received")

    body = await request.json()
    device_id = body.get("device_id")
    brand_id = body.get("brand_id")

    logger.info(f"Requesting models for device: {device_id}, brand: {brand_id}")

    models_data = load_fixture("device_models.json")

    # Filter models based on device_id and brand_id
    all_models = models_data.get("data", [])
    filtered_models = []

    for model in all_models:
        # If device_id is provided, filter by it, otherwise show all
        device_match = not device_id or model.get("device_id") == device_id
        # If brand_id is provided, filter by it, otherwise show all
        brand_match = not brand_id or model.get("brand_id") == brand_id

        if device_match and brand_match:
            filtered_models.append(model)

    # If no models found for specific device, return all models from TEST_DEVICE_001 as fallback
    if not filtered_models and device_id:
        logger.info(f"No models found for device {device_id}, using fallback device TEST_DEVICE_001")
        for model in all_models:
            if model.get("device_id") == "TEST_DEVICE_001":
                # Update the device_id to match the requested one for frontend consistency
                model_copy = model.copy()
                model_copy["device_id"] = device_id
                filtered_models.append(model_copy)

    logger.info(f"Returning {len(filtered_models)} models")
    return mock_response(filtered_models)

@app.post("/mobileShell/en/order/payData")
async def send_payment_data(request: Request, authorization: str = Header(None)):
    """Mock payment data endpoint"""
    logger.info("Mock payment data request received")

    body = await request.json()
    third_id = body.get("third_id")

    payment_data = load_fixture("payment_responses.json")

    # Generate mock Chinese payment ID
    chinese_payment_id = f"MSPY{int(time.time())}{third_id[-6:]}"

    # Store payment status as waiting
    payment_statuses[third_id] = {
        "status": 1,  # waiting
        "chinese_payment_id": chinese_payment_id,
        "created_at": time.time()
    }

    response_data = payment_data.get("payData_success", {})
    if response_data.get("data"):
        response_data["data"]["id"] = chinese_payment_id

    logger.info(f"Mock payment created: {third_id} -> {chinese_payment_id}")
    return mock_response(response_data.get("data", {"id": chinese_payment_id}))

@app.post("/mobileShell/en/order/getPayStatus")
async def get_payment_status(request: Request, authorization: str = Header(None)):
    """Mock payment status endpoint"""
    logger.info("Mock payment status request received")

    body = await request.json()
    third_ids = body if isinstance(body, list) else [body]

    payment_data = load_fixture("payment_responses.json")
    status_template = payment_data.get("payStatus_success", {}).get("data", [])

    result = []
    for third_id in third_ids:
        if third_id in payment_statuses:
            status_info = payment_statuses[third_id]
            status_item = {
                "third_id": third_id,
                "status": status_info["status"],
                "chinese_payment_id": status_info["chinese_payment_id"]
            }
            result.append(status_item)
        else:
            # Return waiting status for unknown IDs
            result.append({
                "third_id": third_id,
                "status": 1,  # waiting
                "chinese_payment_id": f"MSPY_UNKNOWN_{third_id}"
            })

    logger.info(f"Returning payment status for {len(result)} items")
    return mock_response(result)

@app.post("/mobileShell/en/order/orderData")
async def send_order_data(request: Request, authorization: str = Header(None)):
    """Mock order data endpoint - triggers webhook simulation"""
    logger.info("Mock order data request received")

    body = await request.json()
    third_id = body.get("third_id")
    third_pay_id = body.get("third_pay_id")

    order_data = load_fixture("payment_responses.json")

    # Generate mock queue number
    queue_no = f"Q{int(time.time())}{third_id[-4:]}"

    # Store order status
    order_statuses[third_id] = {
        "status": "pending",
        "queue_no": queue_no,
        "created_at": time.time()
    }

    # Update payment status to paid
    if third_id in payment_statuses:
        payment_statuses[third_id]["status"] = 3  # paid

    # Simulate webhook to backend
    webhook_url = "http://localhost:8000/api/chinese/order-status-update"

    # Send "printing" status immediately
    printing_payload = {
        "order_id": third_id,
        "status": "printing",
        "queue_number": queue_no,
        "chinese_order_id": f"CHN_{queue_no}",
        "estimated_completion": "2-3 minutes"
    }
    send_webhook_async(webhook_url, printing_payload, delay=1)

    # Send "completed" status after 5 seconds
    completed_payload = {
        "order_id": third_id,
        "status": "completed",
        "queue_number": queue_no,
        "chinese_order_id": f"CHN_{queue_no}",
        "notes": "Phone case printed successfully"
    }
    send_webhook_async(webhook_url, completed_payload, delay=5)

    response_data = order_data.get("orderData_success", {})
    if response_data.get("data"):
        response_data["data"]["queue_no"] = queue_no

    logger.info(f"Mock order created: {third_id} -> {queue_no}")
    return mock_response(response_data.get("data", {"queue_no": queue_no}))

@app.post("/mobileShell/en/order/getOrderStatus")
async def get_order_status(request: Request, authorization: str = Header(None)):
    """Mock order status endpoint"""
    logger.info("Mock order status request received")

    body = await request.json()
    third_ids = body if isinstance(body, list) else [body]

    result = []
    for third_id in third_ids:
        if third_id in order_statuses:
            status_info = order_statuses[third_id]
            status_item = {
                "third_id": third_id,
                "status": status_info["status"],
                "queue_no": status_info["queue_no"]
            }
            result.append(status_item)
        else:
            result.append({
                "third_id": third_id,
                "status": "pending",
                "queue_no": "UNKNOWN"
            })

    logger.info(f"Returning order status for {len(result)} items")
    return mock_response(result)

# Special endpoint to manually update payment status (for testing)
@app.post("/mock/update-payment-status")
async def update_payment_status(request: Request):
    """Mock endpoint to manually update payment status"""
    body = await request.json()
    third_id = body.get("third_id")
    status = body.get("status", 3)  # default to paid

    if third_id in payment_statuses:
        payment_statuses[third_id]["status"] = status
        logger.info(f"Updated payment status for {third_id} to {status}")
        return {"success": True, "message": f"Updated {third_id} to status {status}"}
    else:
        return {"success": False, "message": f"Payment {third_id} not found"}

if __name__ == "__main__":
    logger.info("Starting Chinese API Mock Server on port 8001")
    logger.info("Mock mode active - blocking real network calls")
    uvicorn.run(app, host="0.0.0.0", port=8001)