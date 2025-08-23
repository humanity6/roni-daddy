#!/usr/bin/env python3
"""
TEST IMAGE URL ISSUE
The Chinese API might be failing because of image URL issues.
Let's test different image URL formats to see what works.
"""

import requests
import json
import time
from datetime import datetime

def log_with_timestamp(message):
    """Log message with precise timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")

def test_different_image_urls():
    """Test orderData with different image URL formats"""
    
    log_with_timestamp("🔍 TESTING IMAGE URL FORMATS")
    log_with_timestamp("The Chinese API might be rejecting our image URLs")
    log_with_timestamp("=" * 70)
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "CXYLOGD8OQUK"
    
    # Generate payment first
    now = datetime.now()
    date_str = f"{now.year % 100:02d}{now.month:02d}{now.day:02d}"
    timestamp_suffix = str(int(time.time() * 1000))[-6:]
    third_id = f"PYEN{date_str}{timestamp_suffix}"
    
    log_with_timestamp(f"🆔 Creating payment: {third_id}")
    
    # Step 1: Create payment
    pay_data = {
        "third_id": third_id,
        "pay_amount": 19.99,
        "pay_type": 5,
        "mobile_model_id": "MM1020250226000002",
        "device_id": device_id
    }
    
    try:
        pay_response = requests.post(
            f"{base_url}/api/chinese/order/payData",
            json=pay_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if not (pay_response.ok and pay_response.json().get('code') == 200):
            log_with_timestamp("❌ PayData failed, cannot test image URLs")
            return False
            
        chinese_payment_id = pay_response.json()['data']['id']
        log_with_timestamp(f"✅ Payment created: {chinese_payment_id}")
        
        # Test different image URL formats
        image_url_tests = [
            {
                "name": "Current format (with token)",
                "url": "https://pimpmycase.onrender.com/image/test-image.jpg?token=1234567890:end_user:abcdef123456"
            },
            {
                "name": "Simple public URL (no token)",
                "url": "https://pimpmycase.onrender.com/uploads/test-image.jpg"
            },
            {
                "name": "Different domain (httpbin for testing)",
                "url": "https://httpbin.org/image/jpeg"
            },
            {
                "name": "Local relative path",
                "url": "/uploads/test-image.jpg"
            },
            {
                "name": "Empty/null image",
                "url": ""
            },
            {
                "name": "Very simple image URL",
                "url": "https://via.placeholder.com/300x400.jpg"
            }
        ]
        
        for i, test in enumerate(image_url_tests, 1):
            log_with_timestamp(f"\n🧪 TEST {i}: {test['name']}")
            log_with_timestamp(f"📷 Image URL: {test['url']}")
            
            # Create new order for each test
            order_third_id = f"OREN{date_str}{str(int(time.time() * 1000))[-6:]}"
            
            order_data = {
                "third_pay_id": third_id,
                "third_id": order_third_id,
                "mobile_model_id": "MM1020250226000002",
                "pic": test['url'],
                "device_id": device_id
            }
            
            try:
                order_response = requests.post(
                    f"{base_url}/api/chinese/order/orderData",
                    json=order_data,
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                
                if order_response.ok:
                    result = order_response.json()
                    debug_info = result.get('_debug', {})
                    pic_had_query = debug_info.get('pic_had_query', False)
                    
                    log_with_timestamp(f"📊 Result code: {result.get('code')}")
                    log_with_timestamp(f"📝 Message: {result.get('msg')}")
                    log_with_timestamp(f"🔍 Pic had query params: {pic_had_query}")
                    
                    if result.get('code') == 200:
                        log_with_timestamp(f"🎉 SUCCESS! Working image URL format: {test['name']}")
                        log_with_timestamp(f"✅ URL: {test['url']}")
                        return True
                    else:
                        log_with_timestamp(f"❌ Failed with: {result.get('msg')}")
                        
                        # Check for specific image-related errors
                        error_msg = result.get('msg', '').lower()
                        if 'image' in error_msg or 'pic' in error_msg or 'url' in error_msg:
                            log_with_timestamp(f"🚨 IMAGE-RELATED ERROR detected!")
                        elif 'payment information does not exist' in error_msg:
                            log_with_timestamp(f"⚠️ Same payment error - not image related")
                else:
                    log_with_timestamp(f"❌ HTTP error: {order_response.status_code}")
                    
            except Exception as e:
                log_with_timestamp(f"❌ Exception: {e}")
            
            log_with_timestamp("-" * 50)
            time.sleep(1)  # Small delay between tests
        
        log_with_timestamp(f"\n💥 NO WORKING IMAGE URL FORMAT FOUND")
        log_with_timestamp(f"🔍 The issue might not be image URL related")
        return False
        
    except Exception as e:
        log_with_timestamp(f"❌ PayData exception: {e}")
        return False

def test_chinese_api_requirements():
    """Test what the Chinese API actually expects"""
    
    log_with_timestamp(f"\n🔍 TESTING CHINESE API REQUIREMENTS")
    log_with_timestamp("Let's test minimal orderData to see what's required")
    log_with_timestamp("=" * 60)
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "CXYLOGD8OQUK"
    
    # Create a fresh payment for testing
    now = datetime.now()
    date_str = f"{now.year % 100:02d}{now.month:02d}{now.day:02d}"
    timestamp_suffix = str(int(time.time() * 1000))[-6:]
    third_id = f"PYEN{date_str}{timestamp_suffix}"
    
    pay_data = {
        "third_id": third_id,
        "pay_amount": 19.99,
        "pay_type": 5,
        "mobile_model_id": "MM1020250226000002",
        "device_id": device_id
    }
    
    try:
        # Create payment
        pay_response = requests.post(f"{base_url}/api/chinese/order/payData", json=pay_data, timeout=30)
        
        if pay_response.ok and pay_response.json().get('code') == 200:
            log_with_timestamp(f"✅ Fresh payment created: {third_id}")
            
            # Test with minimal required fields only
            order_third_id = f"OREN{date_str}{str(int(time.time() * 1000))[-6:]}"
            
            minimal_order = {
                "third_pay_id": third_id,
                "third_id": order_third_id,
                "mobile_model_id": "MM1020250226000002",
                "device_id": device_id
                # Deliberately omitting 'pic' field
            }
            
            log_with_timestamp(f"🧪 Testing minimal orderData (no pic field)...")
            log_with_timestamp(f"📋 Payload: {json.dumps(minimal_order, indent=2)}")
            
            order_response = requests.post(f"{base_url}/api/chinese/order/orderData", json=minimal_order, timeout=60)
            
            if order_response.ok:
                result = order_response.json()
                log_with_timestamp(f"📊 Result: {result.get('code')} - {result.get('msg')}")
                
                if result.get('code') == 200:
                    log_with_timestamp(f"🎉 SUCCESS! Pic field is not required!")
                    return True
                else:
                    log_with_timestamp(f"❌ Still failed: {result.get('msg')}")
                    return False
            else:
                log_with_timestamp(f"❌ HTTP error: {order_response.status_code}")
                return False
        else:
            log_with_timestamp(f"❌ Could not create test payment")
            return False
            
    except Exception as e:
        log_with_timestamp(f"❌ Exception: {e}")
        return False

def main():
    """Main test function"""
    
    log_with_timestamp("🚀 IMAGE URL ISSUE INVESTIGATION")
    log_with_timestamp("Testing different image formats to isolate the orderData failure")
    log_with_timestamp("=" * 80)
    
    # Test 1: Different image URL formats
    success = test_different_image_urls()
    
    if not success:
        # Test 2: Minimal requirements
        log_with_timestamp(f"\n🔄 TRYING DIFFERENT APPROACH...")
        minimal_success = test_chinese_api_requirements()
        
        if minimal_success:
            success = True
    
    log_with_timestamp(f"\n" + "=" * 80)
    log_with_timestamp("🏁 IMAGE URL INVESTIGATION COMPLETE")
    
    if success:
        log_with_timestamp("✅ Found the issue or a working format!")
    else:
        log_with_timestamp("❌ Image URL is not the issue")
        log_with_timestamp("💡 The problem is likely deeper in the API integration")
        log_with_timestamp("🔧 Next steps: Check Chinese API logs or contact their team")

if __name__ == "__main__":
    main()