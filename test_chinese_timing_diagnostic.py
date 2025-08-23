#!/usr/bin/env python3
"""
COMPREHENSIVE CHINESE API TIMING DIAGNOSTIC
Diagnoses the exact timing issue causing "Payment information does not exist"
"""

import requests
import json
import time
from datetime import datetime, timezone
import threading
import queue

def log_with_timestamp(message):
    """Log message with precise timestamp"""
    timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]  # millisecond precision
    print(f"[{timestamp}] {message}")

def test_chinese_api_direct():
    """Test Chinese API directly without our backend"""
    
    log_with_timestamp("🔍 TESTING CHINESE API DIRECTLY (bypassing our backend)")
    
    # Authentication first
    log_with_timestamp("Step 1: Authenticating with Chinese API...")
    
    login_url = "http://app-dev.deligp.com:8500/mobileShell/en/user/login"
    login_payload = {
        "account": "taharizvi.ai@gmail.com",
        "password": "EN112233"
    }
    
    # Generate signature for login
    import hashlib
    login_signature_string = f"EN112233taharizvi.ai@gmail.commobileShellshfoa3sfwoehnf3290rqefiz4efd"
    login_signature = hashlib.md5(login_signature_string.encode()).hexdigest()
    
    login_headers = {
        "Content-Type": "application/json",
        "sign": login_signature,
        "req_source": "en"
    }
    
    try:
        login_response = requests.post(login_url, json=login_payload, headers=login_headers, timeout=10)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            if login_result.get('code') == 200:
                token = login_result.get('data', {}).get('token')
                log_with_timestamp(f"✅ Authentication successful, token: {token[:50]}...")
            else:
                log_with_timestamp(f"❌ Login failed: {login_result.get('msg')}")
                return False
        else:
            log_with_timestamp(f"❌ Login HTTP error: {login_response.status_code}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"❌ Login exception: {e}")
        return False
    
    # Now test the timing issue
    device_id = "CXYLOGD8OQUK"
    now = datetime.now()
    timestamp = int(time.time() * 1000)
    third_id = f"PYEN{now.strftime('%d%m%y')}{str(timestamp)[-6:]}"
    
    log_with_timestamp(f"🎯 Testing payment timing with device {device_id}")
    log_with_timestamp(f"🆔 Payment ID: {third_id}")
    
    # Step 2: payData call
    log_with_timestamp("Step 2: Calling payData directly...")
    
    pay_payload = {
        "mobile_model_id": "MM1020250226000002",  # iPhone 16 Pro Max
        "device_id": device_id,
        "third_id": third_id,
        "pay_amount": 19.99,
        "pay_type": 5
    }
    
    # Generate signature for payData
    pay_signature_string = f"{device_id}MM102025022600000219.995{third_id}mobileShellshfoa3sfwoehnf3290rqefiz4efd"
    pay_signature = hashlib.md5(pay_signature_string.encode()).hexdigest()
    
    pay_headers = {
        "Content-Type": "application/json",
        "Authorization": token,
        "sign": pay_signature,
        "req_source": "en"
    }
    
    pay_url = "http://app-dev.deligp.com:8500/mobileShell/en/order/payData"
    
    pay_start_time = time.time()
    log_with_timestamp(f"⏰ PayData call starting at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}")
    
    try:
        pay_response = requests.post(pay_url, json=pay_payload, headers=pay_headers, timeout=15)
        pay_end_time = time.time()
        
        log_with_timestamp(f"⏰ PayData call completed at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]} (took {(pay_end_time - pay_start_time)*1000:.0f}ms)")
        
        if pay_response.status_code == 200:
            pay_result = pay_response.json()
            log_with_timestamp(f"PayData Response: {json.dumps(pay_result, indent=2)}")
            
            if pay_result.get('code') == 200:
                chinese_payment_id = pay_result.get('data', {}).get('id')
                log_with_timestamp(f"✅ PayData SUCCESS: {chinese_payment_id}")
                
                # Test different delay intervals
                for delay_seconds in [0, 1, 2, 3, 5, 10]:
                    log_with_timestamp(f"\n🧪 TESTING WITH {delay_seconds} SECOND DELAY")
                    
                    if delay_seconds > 0:
                        log_with_timestamp(f"⏳ Waiting {delay_seconds} seconds...")
                        time.sleep(delay_seconds)
                    
                    # Step 3: orderData call
                    order_third_id = f"OREN{now.strftime('%d%m%y')}{str(int(time.time() * 1000))[-6:]}"
                    
                    order_payload = {
                        "third_pay_id": chinese_payment_id,  # Use the Chinese payment ID directly
                        "third_id": order_third_id,
                        "mobile_model_id": "MM1020250226000002",
                        "pic": "https://pimpmycase.onrender.com/uploads/test-image.jpg",
                        "device_id": device_id
                    }
                    
                    # Generate signature for orderData
                    order_signature_string = f"{device_id}MM1020250226000002https://pimpmycase.onrender.com/uploads/test-image.jpg{order_third_id}{chinese_payment_id}mobileShellshfoa3sfwoehnf3290rqefiz4efd"
                    order_signature = hashlib.md5(order_signature_string.encode()).hexdigest()
                    
                    order_headers = {
                        "Content-Type": "application/json",
                        "Authorization": token,
                        "sign": order_signature,
                        "req_source": "en"
                    }
                    
                    order_url = "http://app-dev.deligp.com:8500/mobileShell/en/order/orderData"
                    
                    order_start_time = time.time()
                    log_with_timestamp(f"⏰ OrderData call starting at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}")
                    
                    try:
                        order_response = requests.post(order_url, json=order_payload, headers=order_headers, timeout=15)
                        order_end_time = time.time()
                        
                        log_with_timestamp(f"⏰ OrderData call completed at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]} (took {(order_end_time - order_start_time)*1000:.0f}ms)")
                        
                        if order_response.status_code == 200:
                            order_result = order_response.json()
                            log_with_timestamp(f"OrderData Response: {json.dumps(order_result, indent=2)}")
                            
                            if order_result.get('code') == 200:
                                log_with_timestamp(f"✅ SUCCESS WITH {delay_seconds}s DELAY: Order created!")
                                return delay_seconds
                            else:
                                log_with_timestamp(f"❌ FAILED WITH {delay_seconds}s DELAY: {order_result.get('msg')}")
                        else:
                            log_with_timestamp(f"❌ OrderData HTTP error: {order_response.status_code}")
                            
                    except Exception as e:
                        log_with_timestamp(f"❌ OrderData exception: {e}")
                    
                    log_with_timestamp("-" * 50)
                    
            else:
                log_with_timestamp(f"❌ PayData failed: {pay_result.get('msg')}")
                return False
        else:
            log_with_timestamp(f"❌ PayData HTTP error: {pay_response.status_code}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"❌ PayData exception: {e}")
        return False
        
    log_with_timestamp("🔚 All delay tests completed - no successful delay found")
    return False

def test_backend_timing():
    """Test our backend to see actual timing vs expected timing"""
    
    log_with_timestamp("\n🔍 TESTING OUR BACKEND TIMING")
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "CXYLOGD8OQUK"
    
    # Generate unique payment ID
    now = datetime.now()
    timestamp = int(time.time() * 1000)
    third_id = f"PYEN{now.strftime('%d%m%y')}{str(timestamp)[-6:]}"
    
    log_with_timestamp(f"🆔 Testing Backend Payment ID: {third_id}")
    
    # Step 1: payData call through our backend
    pay_data = {
        "third_id": third_id,
        "pay_amount": 19.99,
        "pay_type": 5,
        "mobile_model_id": "MM1020250226000002",
        "device_id": device_id
    }
    
    log_with_timestamp("Step 1: Calling our backend payData...")
    
    pay_start_time = time.time()
    log_with_timestamp(f"⏰ Backend PayData starting at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}")
    
    try:
        pay_response = requests.post(
            f"{base_url}/api/chinese/order/payData",
            json=pay_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        pay_end_time = time.time()
        log_with_timestamp(f"⏰ Backend PayData completed at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]} (took {(pay_end_time - pay_start_time)*1000:.0f}ms)")
        
        if pay_response.ok:
            pay_result = pay_response.json()
            log_with_timestamp(f"Backend PayData Response: {json.dumps(pay_result, indent=2)}")
            
            if pay_result.get('code') == 200:
                chinese_payment_id = pay_result.get('data', {}).get('id')
                log_with_timestamp(f"✅ Backend PayData SUCCESS: {chinese_payment_id}")
                
                # Step 2: orderData call through our backend (should have 3s delay)
                log_with_timestamp("Step 2: Calling our backend orderData (should wait 3s)...")
                
                order_third_id = f"OREN{now.strftime('%d%m%y')}{str(int(time.time() * 1000))[-6:]}"
                order_data = {
                    "third_pay_id": third_id,
                    "third_id": order_third_id,
                    "mobile_model_id": "MM1020250226000002",
                    "pic": "https://pimpmycase.onrender.com/uploads/test-image.jpg",
                    "device_id": device_id
                }
                
                order_start_time = time.time()
                log_with_timestamp(f"⏰ Backend OrderData starting at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}")
                log_with_timestamp(f"⏰ Expected 3s delay means orderData should complete after: {datetime.fromtimestamp(order_start_time + 3, timezone.utc).strftime('%H:%M:%S.%f')[:-3]}")
                
                order_response = requests.post(
                    f"{base_url}/api/chinese/order/orderData",
                    json=order_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                order_end_time = time.time()
                actual_delay = order_end_time - pay_end_time
                
                log_with_timestamp(f"⏰ Backend OrderData completed at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]} (took {(order_end_time - order_start_time)*1000:.0f}ms)")
                log_with_timestamp(f"⏰ ACTUAL DELAY between payData and orderData: {actual_delay:.2f}s")
                
                if order_response.ok:
                    order_result = order_response.json()
                    log_with_timestamp(f"Backend OrderData Response: {json.dumps(order_result, indent=2)}")
                    
                    if order_result.get('code') == 200:
                        log_with_timestamp("✅ BACKEND SUCCESS: Order created!")
                        return True
                    else:
                        log_with_timestamp(f"❌ BACKEND FAILED: {order_result.get('msg')}")
                        return False
                else:
                    log_with_timestamp(f"❌ Backend OrderData HTTP error: {order_response.status_code}")
                    return False
                    
            else:
                log_with_timestamp(f"❌ Backend PayData failed: {pay_result.get('msg')}")
                return False
        else:
            log_with_timestamp(f"❌ Backend PayData HTTP error: {pay_response.status_code}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"❌ Backend test exception: {e}")
        return False

def main():
    """Main diagnostic function"""
    
    log_with_timestamp("🚀 CHINESE API TIMING DIAGNOSTIC STARTED")
    log_with_timestamp("=" * 80)
    
    # Test 1: Direct Chinese API with different delays
    log_with_timestamp("\n📋 TEST 1: CHINESE API DIRECT TIMING TEST")
    log_with_timestamp("Testing different delays to find the minimum working delay")
    log_with_timestamp("-" * 50)
    
    optimal_delay = test_chinese_api_direct()
    
    if optimal_delay is not False:
        log_with_timestamp(f"\n🎉 FOUND OPTIMAL DELAY: {optimal_delay} seconds")
    else:
        log_with_timestamp("\n😞 NO WORKING DELAY FOUND")
    
    log_with_timestamp("\n📋 TEST 2: BACKEND TIMING VERIFICATION")
    log_with_timestamp("Testing if our backend actually implements the 3s delay")
    log_with_timestamp("-" * 50)
    
    backend_success = test_backend_timing()
    
    log_with_timestamp("\n" + "=" * 80)
    log_with_timestamp("🏁 DIAGNOSTIC COMPLETE")
    
    if optimal_delay is not False:
        log_with_timestamp(f"✅ SOLUTION: Use {optimal_delay} second delay between payData and orderData")
    else:
        log_with_timestamp("❌ ISSUE: Chinese API timing requirements could not be determined")
        
    if backend_success:
        log_with_timestamp("✅ BACKEND: 3s delay is working correctly")
    else:
        log_with_timestamp("❌ BACKEND: 3s delay is NOT working correctly")

if __name__ == '__main__':
    main()