#!/usr/bin/env python3
"""
Test the Chinese API timing fix directly
Tests payData -> 3 second delay -> orderData sequence
"""

import requests
import json
import time
from datetime import datetime

def test_timing_fix():
    """Test the Chinese API with proper timing"""
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "CXYLOGD8OQUK"  # Working device ID
    
    # Generate unique payment ID
    now = datetime.now()
    timestamp = int(time.time() * 1000)
    third_id = f"PYEN{now.strftime('%d%m%y')}{str(timestamp)[-6:]}"
    
    print(f"Testing Chinese API timing fix...")
    print(f"Device ID: {device_id}")
    print(f"Payment ID: {third_id}")
    print()
    
    # Step 1: payData call
    pay_data = {
        "third_id": third_id,
        "pay_amount": 4.99,
        "pay_type": 5,  # Vending machine payment (must be 5, 6, or 12)
        "mobile_model_id": "62",  # iPhone 15 Pro
        "device_id": device_id
    }
    
    print("Step 1: Calling payData...")
    print(f"Payload: {json.dumps(pay_data, indent=2)}")
    
    try:
        pay_response = requests.post(
            f"{base_url}/api/chinese/order/payData",
            json=pay_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"PayData Response Status: {pay_response.status_code}")
        
        if pay_response.ok:
            pay_result = pay_response.json()
            print(f"PayData Response: {json.dumps(pay_result, indent=2)}")
            
            if pay_result.get('code') == 200:
                chinese_payment_id = pay_result.get('data', {}).get('id')
                print(f"SUCCESS: Chinese Payment ID: {chinese_payment_id}")
                
                # Step 2: 3 second delay (the critical fix)
                print("\nStep 2: Waiting 3 seconds for Chinese API to process payment...")
                time.sleep(3)
                
                # Step 3: orderData call
                order_third_id = f"OREN{now.strftime('%d%m%y')}{str(int(time.time() * 1000))[-6:]}"
                order_data = {
                    "third_pay_id": third_id,
                    "third_id": order_third_id,
                    "mobile_model_id": "62",
                    "pic": "https://pimpmycase.onrender.com/uploads/test-image.jpg",  # Valid image URL
                    "device_id": device_id
                }
                
                print("Step 3: Calling orderData...")
                print(f"Payload: {json.dumps(order_data, indent=2)}")
                
                order_response = requests.post(
                    f"{base_url}/api/chinese/order/orderData",
                    json=order_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                print(f"OrderData Response Status: {order_response.status_code}")
                
                if order_response.ok:
                    order_result = order_response.json()
                    print(f"OrderData Response: {json.dumps(order_result, indent=2)}")
                    
                    if order_result.get('code') == 200:
                        print("\n✅ SUCCESS: Complete flow worked with timing fix!")
                        print(f"Chinese Order ID: {order_result.get('data', {}).get('id')}")
                        return True
                    else:
                        print(f"\n❌ OrderData failed: {order_result.get('msg')}")
                        return False
                else:
                    error_text = order_response.text
                    print(f"\n❌ OrderData HTTP error: {error_text}")
                    return False
                    
            else:
                print(f"\n❌ PayData failed: {pay_result.get('msg')}")
                return False
        else:
            error_text = pay_response.text
            print(f"\n❌ PayData HTTP error: {error_text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return False

if __name__ == '__main__':
    success = test_timing_fix()
    if success:
        print("\n🎉 TIMING FIX VERIFICATION COMPLETE - The 3-second delay solved the issue!")
    else:
        print("\n💥 TIMING FIX NEEDS MORE WORK - Issue may still persist")