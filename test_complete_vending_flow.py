#!/usr/bin/env python3
"""
Test the complete vending machine flow including session registration
"""

import requests
import json
from datetime import datetime
import time
import random
import string

def generate_session_id(machine_id: str) -> str:
    """Generate session ID following the Chinese format"""
    now = datetime.now()
    date = now.strftime('%Y%m%d')
    time_str = now.strftime('%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{machine_id}_{date}_{time_str}_{random_suffix}"

def test_complete_vending_flow():
    """Test the complete vending machine flow"""
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "10HKNTDOH2BA"
    session_id = generate_session_id(device_id)
    
    print("=== Testing Complete Vending Machine Flow ===")
    print(f"Base URL: {base_url}")
    print(f"Device ID: {device_id}")
    print(f"Session ID: {session_id}")
    print()
    
    # Step 1: Register user with session
    print("Step 1: Registering user with session...")
    
    register_data = {
        "machine_id": device_id,
        "session_id": session_id,
        "location": "Test Environment",
        "user_agent": "Test-Agent/1.0",
        "ip_address": "127.0.0.1"
    }
    
    try:
        register_response = requests.post(
            f"{base_url}/api/vending/session/{session_id}/register-user",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Registration Status: {register_response.status_code}")
        if register_response.status_code != 200:
            print(f"Registration Error: {register_response.text}")
            return False
        else:
            print("✅ User registration successful")
            
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False
    
    # Step 2: Get available phone models for testing
    print("\nStep 2: Getting iPhone models...")
    
    try:
        models_response = requests.get(
            f"{base_url}/api/brands/iphone/models",
            params={"device_id": device_id},
            timeout=30
        )
        
        print(f"Models Status: {models_response.status_code}")
        if models_response.status_code != 200:
            print(f"Models Error: {models_response.text}")
            return False
        
        models_data = models_response.json()
        if not models_data or len(models_data) == 0:
            print("❌ No iPhone models available")
            return False
        
        # Use the first available model
        test_model = models_data[0]
        print(f"✅ Using test model: {test_model['name']} (ID: {test_model['chinese_model_id']})")
        
    except Exception as e:
        print(f"❌ Failed to get models: {e}")
        return False
    
    # Step 3: Send order summary
    print("\nStep 3: Sending order summary...")
    
    order_summary_data = {
        "session_id": session_id,
        "order_data": {
            "brand": "iPhone",
            "brand_id": "BR20250111000002",
            "model": test_model["name"],
            "template": "basic",
            "color": "Natural Titanium",
            "inputText": "Test Case",
            "selectedFont": "Arial",
            "selectedTextColor": "#000000",
            "images": [],
            "colors": [],
            "price": float(test_model["price"]),
            "chinese_model_id": test_model["chinese_model_id"],
            "device_id": device_id
        },
        "payment_amount": float(test_model["price"]),
        "currency": "GBP"
    }
    
    try:
        order_response = requests.post(
            f"{base_url}/api/vending/session/{session_id}/order-summary",
            json=order_summary_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Order Summary Status: {order_response.status_code}")
        if order_response.status_code != 200:
            print(f"Order Summary Error: {order_response.text}")
            return False
        else:
            print("✅ Order summary created successfully")
            
    except Exception as e:
        print(f"❌ Order summary failed: {e}")
        return False
    
    # Step 4: Test Chinese payment endpoint
    print("\nStep 4: Testing Chinese payment endpoint...")
    
    payment_data = {
        "mobile_model_id": test_model["chinese_model_id"],
        "device_id": device_id,
        "third_id": f"PYEN{datetime.now().strftime('%y%m%d')}{str(int(time.time()))[-6:]}",
        "pay_amount": float(test_model["price"]),
        "pay_type": 5  # Vending machine
    }
    
    try:
        payment_response = requests.post(
            f"{base_url}/api/chinese/order/payData",
            json=payment_data,
            headers={
                "Content-Type": "application/json",
                "X-Correlation-ID": f"TEST_{int(time.time())}"
            },
            timeout=30
        )
        
        print(f"Payment Status: {payment_response.status_code}")
        print(f"Payment Response: {payment_response.text}")
        
        if payment_response.status_code == 200:
            try:
                payment_result = payment_response.json()
                if payment_result.get("code") == 200:
                    print("✅ Payment request successful!")
                    print(f"Chinese Payment ID: {payment_result.get('data', {}).get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ Payment failed: {payment_result.get('msg')}")
                    return False
            except:
                print("❌ Invalid JSON response from payment endpoint")
                return False
        else:
            print(f"❌ Payment request failed with status {payment_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Payment request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_vending_flow()
    print()
    if success:
        print("🎉 Complete vending payment flow test PASSED!")
        print("✅ All fixes are working correctly on Render!")
    else:
        print("💥 Complete vending payment flow test FAILED!")
        print("❌ There may still be issues to resolve.")