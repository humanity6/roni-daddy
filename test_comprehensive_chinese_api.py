#!/usr/bin/env python3
"""
COMPREHENSIVE CHINESE API DIAGNOSTIC
Tests all aspects: timing, third_pay_id format, device_id, and more
"""

import requests
import json
import time
from datetime import datetime, timezone

def log_with_timestamp(message):
    """Log message with precise timestamp"""
    timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")

def test_payment_mapping_flow():
    """Test the complete payment mapping flow through our backend"""
    
    log_with_timestamp("🔍 COMPREHENSIVE CHINESE API FLOW TEST")
    log_with_timestamp("=" * 60)
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "CXYLOGD8OQUK"
    
    # Generate unique payment ID with proper format
    now = datetime.now()
    timestamp = int(time.time() * 1000)
    third_id = f"PYEN{now.strftime('%d%m%y')}{str(timestamp)[-6:]}"
    
    log_with_timestamp(f"🆔 Payment ID (PYEN format): {third_id}")
    log_with_timestamp(f"📱 Device ID: {device_id}")
    log_with_timestamp(f"🏭 Mobile Model: MM1020250226000002 (iPhone 16 Pro Max)")
    
    # Step 1: Call payData
    log_with_timestamp("\n🔸 STEP 1: PAYMENT DATA SUBMISSION")
    
    pay_data = {
        "third_id": third_id,
        "pay_amount": 19.99,
        "pay_type": 5,  # Vending machine
        "mobile_model_id": "MM1020250226000002",
        "device_id": device_id
    }
    
    log_with_timestamp(f"PayData payload: {json.dumps(pay_data, indent=2)}")
    
    try:
        pay_start = time.time()
        pay_response = requests.post(
            f"{base_url}/api/chinese/order/payData",
            json=pay_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        pay_duration = time.time() - pay_start
        
        log_with_timestamp(f"⏱️ PayData took: {pay_duration:.2f}s")
        log_with_timestamp(f"📤 PayData status: {pay_response.status_code}")
        
        if pay_response.ok:
            pay_result = pay_response.json()
            log_with_timestamp(f"📥 PayData response: {json.dumps(pay_result, indent=2)}")
            
            if pay_result.get('code') == 200:
                chinese_payment_id = pay_result.get('data', {}).get('id')
                log_with_timestamp(f"✅ PayData SUCCESS!")
                log_with_timestamp(f"🔄 Mapping: {third_id} -> {chinese_payment_id}")
                
                # Step 2: Test payment mapping storage
                log_with_timestamp("\n🔸 STEP 2: PAYMENT MAPPING VERIFICATION")
                
                # Wait a moment for mapping to be stored
                time.sleep(1)
                
                # Try to verify the mapping exists (if we have an endpoint)
                log_with_timestamp(f"💾 Payment mapping should be stored: {third_id} -> {chinese_payment_id}")
                
                # Step 3: Test orderData with different third_pay_id formats
                log_with_timestamp("\n🔸 STEP 3: ORDER DATA SUBMISSION TESTS")
                
                test_cases = [
                    {
                        "name": "Using original PYEN ID (should be converted to MSPY)",
                        "third_pay_id": third_id
                    },
                    {
                        "name": "Using Chinese MSPY ID directly",
                        "third_pay_id": chinese_payment_id
                    }
                ]
                
                for i, test_case in enumerate(test_cases, 1):
                    log_with_timestamp(f"\n🧪 Test Case {i}: {test_case['name']}")
                    
                    order_third_id = f"OREN{now.strftime('%d%m%y')}{str(int(time.time() * 1000))[-6:]}"
                    
                    order_data = {
                        "third_pay_id": test_case["third_pay_id"],
                        "third_id": order_third_id,
                        "mobile_model_id": "MM1020250226000002",
                        "pic": "https://pimpmycase.onrender.com/uploads/test-image.jpg",
                        "device_id": device_id
                    }
                    
                    log_with_timestamp(f"OrderData payload: {json.dumps(order_data, indent=2)}")
                    
                    try:
                        order_start = time.time()
                        log_with_timestamp(f"⏰ OrderData starting (expecting 3s delay)...")
                        
                        order_response = requests.post(
                            f"{base_url}/api/chinese/order/orderData",
                            json=order_data,
                            headers={"Content-Type": "application/json"},
                            timeout=45  # Longer timeout for 3s delay
                        )
                        
                        order_duration = time.time() - order_start
                        log_with_timestamp(f"⏱️ OrderData took: {order_duration:.2f}s (includes 3s delay)")
                        log_with_timestamp(f"📤 OrderData status: {order_response.status_code}")
                        
                        if order_response.ok:
                            order_result = order_response.json()
                            log_with_timestamp(f"📥 OrderData response: {json.dumps(order_result, indent=2)}")
                            
                            if order_result.get('code') == 200:
                                log_with_timestamp(f"✅ SUCCESS: Order created with {test_case['name']}!")
                                chinese_order_id = order_result.get('data', {}).get('id')
                                queue_no = order_result.get('data', {}).get('queue_no')
                                log_with_timestamp(f"📋 Chinese Order ID: {chinese_order_id}")
                                log_with_timestamp(f"🎯 Queue Number: {queue_no}")
                                return True
                            else:
                                error_msg = order_result.get('msg', 'Unknown error')
                                debug_info = order_result.get('_debug', {})
                                log_with_timestamp(f"❌ FAILED: {error_msg}")
                                log_with_timestamp(f"🐛 Debug info: {json.dumps(debug_info, indent=2)}")
                                
                                # Analyze debug info
                                if debug_info:
                                    attempted_ids = debug_info.get('attempted_third_pay_ids', [])
                                    original_id = debug_info.get('original_third_pay_id')
                                    effective_id = debug_info.get('effective_first_third_pay_id')
                                    
                                    log_with_timestamp(f"🔍 Analysis:")
                                    log_with_timestamp(f"  - Original ID sent: {original_id}")
                                    log_with_timestamp(f"  - Attempted IDs: {attempted_ids}")
                                    log_with_timestamp(f"  - Effective ID used: {effective_id}")
                        else:
                            error_text = order_response.text
                            log_with_timestamp(f"❌ OrderData HTTP error: {order_response.status_code}")
                            log_with_timestamp(f"📄 Error details: {error_text}")
                            
                    except Exception as e:
                        log_with_timestamp(f"❌ OrderData exception: {e}")
                    
                    log_with_timestamp("-" * 40)
                    
                return False
                
            else:
                log_with_timestamp(f"❌ PayData failed: {pay_result.get('msg')}")
                return False
        else:
            error_text = pay_response.text
            log_with_timestamp(f"❌ PayData HTTP error: {pay_response.status_code}")
            log_with_timestamp(f"📄 Error details: {error_text}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"❌ PayData exception: {e}")
        return False

def test_different_delays():
    """Test if longer delays work"""
    
    log_with_timestamp("\n🔍 TESTING DIFFERENT DELAY SCENARIOS")
    log_with_timestamp("=" * 50)
    
    # Test with manual delays between separate calls
    for delay in [5, 10, 15]:
        log_with_timestamp(f"\n🧪 Testing {delay}s manual delay between calls")
        
        base_url = "https://pimpmycase.onrender.com"
        device_id = "CXYLOGD8OQUK"
        
        now = datetime.now()
        timestamp = int(time.time() * 1000)
        third_id = f"PYEN{now.strftime('%d%m%y')}{str(timestamp)[-6:]}"
        
        # Step 1: PayData
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
            
            if pay_response.ok:
                pay_result = pay_response.json()
                if pay_result.get('code') == 200:
                    chinese_payment_id = pay_result.get('data', {}).get('id')
                    log_with_timestamp(f"PayData success: {third_id} -> {chinese_payment_id}")
                    
                    # Manual delay
                    log_with_timestamp(f"⏳ Waiting {delay} seconds...")
                    time.sleep(delay)
                    
                    # Step 2: OrderData  
                    order_third_id = f"OREN{now.strftime('%d%m%y')}{str(int(time.time() * 1000))[-6:]}"
                    order_data = {
                        "third_pay_id": third_id,
                        "third_id": order_third_id,
                        "mobile_model_id": "MM1020250226000002",
                        "pic": "https://pimpmycase.onrender.com/uploads/test-image.jpg",
                        "device_id": device_id
                    }
                    
                    order_response = requests.post(
                        f"{base_url}/api/chinese/order/orderData",
                        json=order_data,
                        headers={"Content-Type": "application/json"},
                        timeout=45
                    )
                    
                    if order_response.ok:
                        order_result = order_response.json()
                        if order_result.get('code') == 200:
                            log_with_timestamp(f"✅ SUCCESS with {delay}s delay!")
                            return delay
                        else:
                            log_with_timestamp(f"❌ Failed with {delay}s delay: {order_result.get('msg')}")
                    else:
                        log_with_timestamp(f"❌ HTTP error with {delay}s delay: {order_response.status_code}")
                else:
                    log_with_timestamp(f"❌ PayData failed for {delay}s test")
            else:
                log_with_timestamp(f"❌ PayData HTTP error for {delay}s test")
                
        except Exception as e:
            log_with_timestamp(f"❌ Exception in {delay}s test: {e}")
            
    return False

def main():
    """Main test function"""
    
    log_with_timestamp("🚀 COMPREHENSIVE CHINESE API DIAGNOSTIC")
    log_with_timestamp("Testing: timing, third_pay_id format, device_id, payment mapping")
    log_with_timestamp("=" * 80)
    
    # Test 1: Complete flow through our backend
    success = test_payment_mapping_flow()
    
    if not success:
        # Test 2: Try different delays
        optimal_delay = test_different_delays()
        if optimal_delay:
            log_with_timestamp(f"\n🎉 Found working delay: {optimal_delay}s")
        else:
            log_with_timestamp("\n😞 No working configuration found")
    else:
        log_with_timestamp("\n🎉 Payment flow working correctly!")
    
    log_with_timestamp("\n" + "=" * 80)
    log_with_timestamp("🏁 COMPREHENSIVE TEST COMPLETE")

if __name__ == '__main__':
    main()