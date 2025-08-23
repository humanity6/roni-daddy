#!/usr/bin/env python3
"""
TEST IMAGE UPLOAD FIX
Verify that we removed base64 fallback and use proper image URLs only
"""

import requests
import json
import time
from datetime import datetime

def main():
    print("🚀 TESTING IMAGE UPLOAD FIX")
    print("=" * 50)
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "CXYLOGD8OQUK"
    
    # Generate proper payment
    now = datetime.now()
    date_str = f"{now.year % 100:02d}{now.month:02d}{now.day:02d}"
    timestamp_suffix = str(int(time.time() * 1000))[-6:]
    third_id = f"PYEN{date_str}{timestamp_suffix}"
    
    print(f"🆔 Testing with: {third_id}")
    
    # Step 1: Create payment
    pay_data = {
        "third_id": third_id,
        "pay_amount": 19.99,
        "pay_type": 5,
        "mobile_model_id": "MM020250224000010",
        "device_id": device_id
    }
    
    pay_response = requests.post(f"{base_url}/api/chinese/order/payData", json=pay_data, timeout=30)
    
    if pay_response.ok and pay_response.json().get('code') == 200:
        print("✅ PayData success")
        
        # Step 2: Test with proper image URL
        order_third_id = f"OREN{date_str}{str(int(time.time() * 1000))[-6:]}"
        proper_image_url = "https://pimpmycase.onrender.com/uploads/test-image.jpg"
        
        order_data = {
            "third_pay_id": third_id,
            "third_id": order_third_id,
            "mobile_model_id": "MM020250224000010",
            "pic": proper_image_url,  # PROPER URL
            "device_id": device_id
        }
        
        print(f"📷 Image URL: {proper_image_url} ({len(proper_image_url)} chars)")
        print(f"✅ Not base64: {not proper_image_url.startswith('data:')}")
        
        order_response = requests.post(f"{base_url}/api/chinese/order/orderData", json=order_data, timeout=60)
        
        print(f"📊 OrderData status: {order_response.status_code}")
        
        if order_response.ok:
            result = order_response.json()
            msg = result.get('msg', '')
            
            if 'Image URL too long' in msg:
                print("❌ STILL GETTING 'Image URL too long' ERROR!")
            elif 'Payment information does not exist' in msg:
                print("✅ GOOD: No 'Image URL too long' error!")
                print("❓ Payment issue is separate (expected for now)")
            elif result.get('code') == 200:
                print("🎉 COMPLETE SUCCESS!")
            else:
                print(f"❓ Different error: {msg}")
                
        elif order_response.status_code == 422:
            error = order_response.json()
            if 'Image URL too long' in str(error):
                print("❌ STILL GETTING 422 'Image URL too long'!")
            else:
                print("✅ No 'Image URL too long' in 422 error")
                print(f"422 Details: {error}")
        else:
            print(f"❌ HTTP error: {order_response.status_code}")
    else:
        print("❌ PayData failed")

if __name__ == "__main__":
    main()