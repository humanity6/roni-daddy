#!/usr/bin/env python3
"""
Test script to validate the complete vending machine payment flow
"""

import requests
import json
from datetime import datetime
import time

def test_vending_payment_flow():
    """Test the complete vending machine payment flow"""
    
    # Use production API URL
    base_url = "https://pimpmycase.onrender.com"
    
    # Test device ID from the logs
    device_id = "10HKNTDOH2BA"
    
    print("=== Testing Vending Machine Payment Flow ===")
    print(f"Base URL: {base_url}")
    print(f"Device ID: {device_id}")
    print()
    
    # Step 1: Test order summary endpoint
    print("Step 1: Testing order summary creation...")
    
    # Generate a test session ID
    session_id = f"{device_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_TEST123"
    
    order_summary_data = {
        "session_id": session_id,
        "order_data": {
            "brand": "iPhone",
            "model": "iPhone 12 mini",
            "chinese_model_id": "MM1020250227000001",
            "device_id": device_id,
            "template": "basic",
            "price": 2.0
        },
        "payment_amount": 2.0,
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
    
    # Step 2: Test Chinese payment endpoint
    print("\nStep 2: Testing Chinese payment endpoint...")
    
    payment_data = {
        "mobile_model_id": "MM1020250227000001",
        "device_id": device_id,
        "third_id": f"PYEN{datetime.now().strftime('%y%m%d')}{str(int(time.time()))[-6:]}",
        "pay_amount": 2.0,
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
            payment_result = payment_response.json()
            if payment_result.get("code") == 200:
                print("✅ Payment request successful")
                return True
            else:
                print(f"❌ Payment failed: {payment_result.get('msg')}")
                return False
        else:
            print(f"❌ Payment request failed with status {payment_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Payment request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_vending_payment_flow()
    if success:
        print("\n🎉 Vending payment flow test PASSED!")
    else:
        print("\n💥 Vending payment flow test FAILED!")