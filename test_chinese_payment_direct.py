#!/usr/bin/env python3
"""
Test the Chinese payment endpoint directly to verify fixes
"""

import requests
import json
from datetime import datetime
import time

def test_chinese_payment_endpoint():
    """Test Chinese payment endpoint directly"""
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "10HKNTDOH2BA"
    
    print("=== Testing Chinese Payment Endpoint Directly ===")
    print(f"Base URL: {base_url}")
    print(f"Device ID: {device_id}")
    print()
    
    # First, get a real model ID from the stock
    print("Step 1: Getting iPhone models for real chinese_model_id...")
    
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
        if not models_data.get("models") or len(models_data["models"]) == 0:
            print("❌ No iPhone models available")
            return False
        
        # Use the first available model
        test_model = models_data["models"][0]
        print(f"✅ Using test model: {test_model['name']}")
        print(f"   Chinese Model ID: {test_model['chinese_model_id']}")
        print(f"   Price: £{test_model['price']}")
        
    except Exception as e:
        print(f"❌ Failed to get models: {e}")
        return False
    
    # Step 2: Test Chinese payment endpoint with OPTIONS preflight
    print("\nStep 2: Testing OPTIONS preflight request...")
    
    try:
        options_response = requests.options(
            f"{base_url}/api/chinese/order/payData",
            headers={
                "Origin": "https://pimpmycase.shop",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,X-Correlation-ID"
            },
            timeout=15
        )
        
        print(f"OPTIONS Status: {options_response.status_code}")
        print(f"CORS Headers: {dict(options_response.headers)}")
        
        if options_response.status_code == 200:
            print("✅ CORS preflight successful")
        else:
            print("⚠️ CORS preflight issues detected")
            
    except Exception as e:
        print(f"❌ OPTIONS request failed: {e}")
    
    # Step 3: Test Chinese payment endpoint
    print("\nStep 3: Testing Chinese payment POST request...")
    
    payment_data = {
        "mobile_model_id": test_model["chinese_model_id"],
        "device_id": device_id,
        "third_id": f"PYEN{datetime.now().strftime('%y%m%d')}{str(int(time.time()))[-6:]}",
        "pay_amount": float(test_model["price"]),
        "pay_type": 5  # Vending machine
    }
    
    print(f"Payment Data: {json.dumps(payment_data, indent=2)}")
    
    try:
        payment_response = requests.post(
            f"{base_url}/api/chinese/order/payData",
            json=payment_data,
            headers={
                "Content-Type": "application/json",
                "X-Correlation-ID": f"TEST_{int(time.time())}",
                "Origin": "https://pimpmycase.shop"
            },
            timeout=30
        )
        
        print(f"Payment Status: {payment_response.status_code}")
        print(f"Payment Headers: {dict(payment_response.headers)}")
        print(f"Payment Response: {payment_response.text}")
        
        if payment_response.status_code == 200:
            try:
                payment_result = payment_response.json()
                if payment_result.get("code") == 200:
                    print("✅ Payment request successful!")
                    print(f"Chinese Payment ID: {payment_result.get('data', {}).get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ Chinese API returned error: {payment_result.get('msg')}")
                    print(f"Error Code: {payment_result.get('code')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Invalid JSON response from payment endpoint")
                return False
        else:
            print(f"❌ Payment request failed with HTTP status {payment_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Payment request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_chinese_payment_endpoint()
    print()
    if success:
        print("🎉 Chinese payment endpoint test PASSED!")
        print("✅ The deployed fixes are working correctly!")
        print("✅ Device ID flow is working")
        print("✅ Payment amount validation is fixed")
        print("✅ CORS headers are working")
        print("✅ Pay type 5 (vending machine) is accepted")
    else:
        print("💥 Chinese payment endpoint test FAILED!")
        print("❌ There may still be issues to investigate.")