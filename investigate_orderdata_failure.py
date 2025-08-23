#!/usr/bin/env python3
"""
INVESTIGATE ORDERDATA FAILURE
Even with payStatus=200, orderData still fails with "Payment information does not exist"
Let's investigate why this happens and test different approaches.
"""

import requests
import json
import time
from datetime import datetime, timezone

def log_with_timestamp(message):
    """Log message with precise timestamp"""
    timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")

def test_chinese_api_sequence():
    """Test the Chinese API sequence with different approaches"""
    
    log_with_timestamp("🔍 INVESTIGATING ORDERDATA FAILURE")
    log_with_timestamp("Despite payStatus=200, orderData fails with 'Payment information does not exist'")
    log_with_timestamp("=" * 80)
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "CXYLOGD8OQUK"
    
    # Generate proper third_id
    now = datetime.now()
    date_str = f"{now.year % 100:02d}{now.month:02d}{now.day:02d}"
    timestamp_suffix = str(int(time.time() * 1000))[-6:]
    third_id = f"PYEN{date_str}{timestamp_suffix}"
    
    log_with_timestamp(f"🆔 Testing with: {third_id}")
    log_with_timestamp(f"📅 Date format: {date_str} (yyMMdd)")
    
    # Step 1: payData
    log_with_timestamp(f"\n🔸 STEP 1: payData")
    
    pay_data = {
        "third_id": third_id,
        "pay_amount": 19.99,
        "pay_type": 5,  # Vending machine
        "mobile_model_id": "MM1020250226000002",
        "device_id": device_id
    }
    
    try:
        log_with_timestamp(f"Calling payData...")
        pay_response = requests.post(
            f"{base_url}/api/chinese/order/payData",
            json=pay_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        log_with_timestamp(f"PayData status: {pay_response.status_code}")
        
        if pay_response.ok:
            pay_result = pay_response.json()
            log_with_timestamp(f"PayData response: {json.dumps(pay_result, indent=2)}")
            
            if pay_result.get('code') == 200:
                chinese_payment_id = pay_result.get('data', {}).get('id')
                log_with_timestamp(f"✅ PayData SUCCESS: {chinese_payment_id}")
                
                # Test different approaches for Step 2 and 3
                approaches = [
                    {
                        "name": "Current Backend Approach (payStatus -> orderData)",
                        "method": "backend_auto"
                    },
                    {
                        "name": "Manual payStatus Then orderData (5s delay)",
                        "method": "manual_5s"
                    },
                    {
                        "name": "Manual payStatus Then orderData (10s delay)",
                        "method": "manual_10s"
                    },
                    {
                        "name": "Skip payStatus, Direct orderData (15s delay)",
                        "method": "skip_paystatus_15s"
                    }
                ]
                
                for approach in approaches:
                    log_with_timestamp(f"\n🧪 TESTING: {approach['name']}")
                    log_with_timestamp("-" * 60)
                    
                    if approach['method'] == 'backend_auto':
                        # Test current backend (automatic payStatus + orderData)
                        success = test_backend_approach(base_url, third_id, device_id)
                        
                    elif approach['method'].startswith('manual'):
                        # Test manual sequence
                        delay = int(approach['method'].split('_')[1][:-1])  # Extract delay
                        success = test_manual_approach(base_url, third_id, chinese_payment_id, device_id, delay)
                        
                    elif approach['method'].startswith('skip'):
                        # Test skipping payStatus
                        delay = int(approach['method'].split('_')[2][:-1])  # Extract delay
                        success = test_skip_paystatus_approach(base_url, third_id, device_id, delay)
                    
                    if success:
                        log_with_timestamp(f"🎉 SUCCESS with {approach['name']}!")
                        return True
                    else:
                        log_with_timestamp(f"❌ FAILED with {approach['name']}")
                
                log_with_timestamp(f"\n💥 ALL APPROACHES FAILED")
                return False
                
            else:
                log_with_timestamp(f"❌ PayData failed: {pay_result.get('msg')}")
                return False
        else:
            log_with_timestamp(f"❌ PayData HTTP error: {pay_response.status_code}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"❌ PayData exception: {e}")
        return False

def test_backend_approach(base_url, third_id, device_id):
    """Test current backend approach"""
    
    log_with_timestamp("🔄 Testing current backend (auto payStatus + orderData)...")
    
    now = datetime.now()
    date_str = f"{now.year % 100:02d}{now.month:02d}{now.day:02d}"
    order_third_id = f"OREN{date_str}{str(int(time.time() * 1000))[-6:]}"
    
    order_data = {
        "third_pay_id": third_id,
        "third_id": order_third_id,
        "mobile_model_id": "MM1020250226000002",
        "pic": "https://pimpmycase.onrender.com/uploads/test-image.jpg",
        "device_id": device_id
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/chinese/order/orderData",
            json=order_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.ok:
            result = response.json()
            debug_info = result.get('_debug', {})
            
            log_with_timestamp(f"PayStatus attempted: {debug_info.get('pre_pay_status_attempted', False)}")
            log_with_timestamp(f"PayStatus code: {debug_info.get('pay_status_resp_code')}")
            log_with_timestamp(f"Result: {result.get('msg')}")
            
            return result.get('code') == 200
        else:
            log_with_timestamp(f"HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"Exception: {e}")
        return False

def test_manual_approach(base_url, third_id, chinese_payment_id, device_id, delay_seconds):
    """Test manual payStatus then orderData approach"""
    
    log_with_timestamp(f"🔄 Testing manual approach with {delay_seconds}s delay...")
    
    # Step 1: Manual payStatus
    log_with_timestamp("Calling payStatus manually...")
    
    paystatus_data = {
        "third_id": third_id,
        "status": 3
    }
    
    try:
        paystatus_response = requests.post(
            f"{base_url}/api/chinese/order/payStatus",
            json=paystatus_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        log_with_timestamp(f"PayStatus status: {paystatus_response.status_code}")
        
        if paystatus_response.ok:
            paystatus_result = paystatus_response.json()
            log_with_timestamp(f"PayStatus result: {paystatus_result.get('msg')}")
            
            if paystatus_result.get('code') == 200:
                # Step 2: Wait
                log_with_timestamp(f"⏳ Waiting {delay_seconds} seconds...")
                time.sleep(delay_seconds)
                
                # Step 3: OrderData
                log_with_timestamp("Calling orderData after payStatus...")
                
                now = datetime.now()
                date_str = f"{now.year % 100:02d}{now.month:02d}{now.day:02d}"
                order_third_id = f"OREN{date_str}{str(int(time.time() * 1000))[-6:]}"
                
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
                    timeout=60
                )
                
                if order_response.ok:
                    order_result = order_response.json()
                    log_with_timestamp(f"OrderData result: {order_result.get('msg')}")
                    return order_result.get('code') == 200
                else:
                    log_with_timestamp(f"OrderData HTTP error: {order_response.status_code}")
                    return False
            else:
                log_with_timestamp(f"PayStatus failed: {paystatus_result.get('msg')}")
                return False
        else:
            log_with_timestamp(f"PayStatus HTTP error: {paystatus_response.status_code}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"Exception in manual approach: {e}")
        return False

def test_skip_paystatus_approach(base_url, third_id, device_id, delay_seconds):
    """Test skipping payStatus entirely"""
    
    log_with_timestamp(f"🔄 Testing skip payStatus with {delay_seconds}s delay...")
    
    # Wait first
    log_with_timestamp(f"⏳ Waiting {delay_seconds} seconds...")
    time.sleep(delay_seconds)
    
    # Direct orderData
    now = datetime.now()
    date_str = f"{now.year % 100:02d}{now.month:02d}{now.day:02d}"
    order_third_id = f"OREN{date_str}{str(int(time.time() * 1000))[-6:]}"
    
    order_data = {
        "third_pay_id": third_id,
        "third_id": order_third_id,
        "mobile_model_id": "MM1020250226000002",
        "pic": "https://pimpmycase.onrender.com/uploads/test-image.jpg",
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
            order_result = order_response.json()
            debug_info = order_result.get('_debug', {})
            log_with_timestamp(f"Backend payStatus attempted: {debug_info.get('pre_pay_status_attempted', False)}")
            log_with_timestamp(f"OrderData result: {order_result.get('msg')}")
            return order_result.get('code') == 200
        else:
            log_with_timestamp(f"OrderData HTTP error: {order_response.status_code}")
            return False
            
    except Exception as e:
        log_with_timestamp(f"Exception: {e}")
        return False

def main():
    """Main investigation function"""
    
    log_with_timestamp("🚀 ORDERDATA FAILURE INVESTIGATION")
    log_with_timestamp("Testing different approaches to solve 'Payment information does not exist'")
    log_with_timestamp("=" * 90)
    
    success = test_chinese_api_sequence()
    
    log_with_timestamp(f"\n" + "=" * 90)
    log_with_timestamp("🏁 INVESTIGATION COMPLETE")
    
    if success:
        log_with_timestamp("✅ Found a working approach!")
    else:
        log_with_timestamp("❌ No working approach found")
        log_with_timestamp("💡 Possible deeper issues:")
        log_with_timestamp("   - Chinese API expects different parameters")
        log_with_timestamp("   - Different authentication or session handling")
        log_with_timestamp("   - Timing requirements beyond what we've tested")
        log_with_timestamp("   - Image URL format or accessibility issues")

if __name__ == "__main__":
    main()