#!/usr/bin/env python3
"""
TEST CHINESE API PAYSTATUS WORKFLOW
The Chinese API documentation mentions a 3-step flow:
1. payData (create payment)
2. payStatus (check payment status) 
3. orderData (create order)

Maybe we need to call payStatus before orderData?
"""

import requests
import json
import time
from datetime import datetime, timezone

def log_with_timestamp(message):
    """Log message with precise timestamp"""
    timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")

def test_paystatus_workflow():
    """Test the complete 3-step workflow with payStatus"""
    
    log_with_timestamp("🔍 TESTING CHINESE API 3-STEP WORKFLOW")
    log_with_timestamp("Step 1: payData → Step 2: payStatus → Step 3: orderData")
    log_with_timestamp("=" * 70)
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "CXYLOGD8OQUK"
    
    # Generate unique payment ID
    now = datetime.now()
    timestamp = int(time.time() * 1000)
    third_id = f"PYEN{now.strftime('%d%m%y')}{str(timestamp)[-6:]}"
    
    log_with_timestamp(f"🆔 Payment ID: {third_id}")
    log_with_timestamp(f"📱 Device ID: {device_id}")
    
    # Step 1: payData
    log_with_timestamp(f"\n🔸 STEP 1: payData")
    
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
        
        log_with_timestamp(f"PayData status: {pay_response.status_code}")
        
        if pay_response.ok:
            pay_result = pay_response.json()
            log_with_timestamp(f"PayData response: {json.dumps(pay_result, indent=2)}")
            
            if pay_result.get('code') == 200:
                chinese_payment_id = pay_result.get('data', {}).get('id')
                log_with_timestamp(f"✅ PayData SUCCESS: {chinese_payment_id}")
                
                # Wait before payStatus
                log_with_timestamp(f"\n⏳ Waiting 2 seconds before payStatus...")
                time.sleep(2)
                
                # Step 2: payStatus - check if this endpoint exists
                log_with_timestamp(f"\n🔸 STEP 2: payStatus (checking payment status)")
                
                # Try different payStatus calls
                paystatus_tests = [
                    {
                        "name": "payStatus with original PYEN ID",
                        "third_id": third_id,
                        "status": 3  # Assuming 3 means "paid" or "completed"
                    },
                    {
                        "name": "payStatus with Chinese MSPY ID", 
                        "third_id": chinese_payment_id,
                        "status": 3
                    }
                ]
                
                successful_paystatus = False
                
                for paystatus_test in paystatus_tests:
                    log_with_timestamp(f"\n🧪 Testing: {paystatus_test['name']}")
                    
                    paystatus_data = {
                        "third_id": paystatus_test["third_id"],
                        "status": paystatus_test["status"]
                    }
                    
                    log_with_timestamp(f"PayStatus payload: {json.dumps(paystatus_data, indent=2)}")
                    
                    try:
                        # Check if payStatus endpoint exists
                        paystatus_response = requests.post(
                            f"{base_url}/api/chinese/order/payStatus",
                            json=paystatus_data,
                            headers={"Content-Type": "application/json"},
                            timeout=30
                        )
                        
                        log_with_timestamp(f"PayStatus status: {paystatus_response.status_code}")
                        
                        if paystatus_response.ok:
                            paystatus_result = paystatus_response.json()
                            log_with_timestamp(f"PayStatus response: {json.dumps(paystatus_result, indent=2)}")
                            
                            if paystatus_result.get('code') == 200:
                                log_with_timestamp(f"✅ PayStatus SUCCESS with {paystatus_test['name']}")
                                successful_paystatus = True
                                break
                            else:
                                log_with_timestamp(f"❌ PayStatus failed: {paystatus_result.get('msg')}")
                        else:
                            error_text = paystatus_response.text
                            log_with_timestamp(f"❌ PayStatus HTTP error: {paystatus_response.status_code}")
                            if paystatus_response.status_code == 404:
                                log_with_timestamp("⚠️ PayStatus endpoint does not exist")
                            else:
                                log_with_timestamp(f"Error details: {error_text}")
                                
                    except Exception as e:
                        log_with_timestamp(f"❌ PayStatus exception: {e}")
                
                # Step 3: orderData (regardless of payStatus result)
                log_with_timestamp(f"\n🔸 STEP 3: orderData")
                log_with_timestamp(f"PayStatus success: {successful_paystatus}")
                
                # Wait before orderData
                log_with_timestamp(f"⏳ Waiting 3 seconds before orderData...")
                time.sleep(3)
                
                order_third_id = f"OREN{now.strftime('%d%m%y')}{str(int(time.time() * 1000))[-6:]}"
                
                order_data = {
                    "third_pay_id": third_id,  # Use original PYEN ID (will be converted)
                    "third_id": order_third_id,
                    "mobile_model_id": "MM1020250226000002",
                    "pic": "https://pimpmycase.onrender.com/uploads/test-image.jpg",
                    "device_id": device_id
                }
                
                log_with_timestamp(f"OrderData payload: {json.dumps(order_data, indent=2)}")
                
                try:
                    order_response = requests.post(
                        f"{base_url}/api/chinese/order/orderData",
                        json=order_data,
                        headers={"Content-Type": "application/json"},
                        timeout=45
                    )
                    
                    log_with_timestamp(f"OrderData status: {order_response.status_code}")
                    
                    if order_response.ok:
                        order_result = order_response.json()
                        log_with_timestamp(f"OrderData response: {json.dumps(order_result, indent=2)}")
                        
                        if order_result.get('code') == 200:
                            log_with_timestamp(f"✅ SUCCESS: Complete 3-step workflow worked!")
                            chinese_order_id = order_result.get('data', {}).get('id')
                            queue_no = order_result.get('data', {}).get('queue_no')
                            log_with_timestamp(f"📋 Chinese Order ID: {chinese_order_id}")
                            log_with_timestamp(f"🎯 Queue Number: {queue_no}")
                            return True
                        else:
                            error_msg = order_result.get('msg')
                            debug_info = order_result.get('_debug', {})
                            log_with_timestamp(f"❌ OrderData failed: {error_msg}")
                            log_with_timestamp(f"🐛 Debug: {json.dumps(debug_info, indent=2)}")
                            
                            if successful_paystatus:
                                log_with_timestamp("⚠️ OrderData failed DESPITE successful payStatus")
                            else:
                                log_with_timestamp("⚠️ OrderData failed, and payStatus also failed/missing")
                            
                            return False
                    else:
                        log_with_timestamp(f"❌ OrderData HTTP error: {order_response.status_code}")
                        return False
                        
                except Exception as e:
                    log_with_timestamp(f"❌ OrderData exception: {e}")
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

def check_chinese_api_documentation():
    """Check what endpoints are available"""
    
    log_with_timestamp("\n🔍 CHECKING AVAILABLE CHINESE API ENDPOINTS")
    log_with_timestamp("=" * 50)
    
    base_url = "https://pimpmycase.onrender.com"
    
    endpoints_to_check = [
        "/api/chinese/order/payData",
        "/api/chinese/order/payStatus", 
        "/api/chinese/order/orderData",
        "/api/chinese/payment/status",
        "/api/chinese/payment/check"
    ]
    
    for endpoint in endpoints_to_check:
        log_with_timestamp(f"\n🔍 Testing endpoint: {endpoint}")
        
        try:
            # Try with minimal payload to check if endpoint exists
            test_payload = {"test": "check"}
            
            response = requests.post(
                f"{base_url}{endpoint}",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 404:
                log_with_timestamp(f"❌ Endpoint does NOT exist: {endpoint}")
            elif response.status_code == 422:
                log_with_timestamp(f"✅ Endpoint EXISTS (validation error expected): {endpoint}")
            elif response.status_code == 400:
                log_with_timestamp(f"✅ Endpoint EXISTS (bad request expected): {endpoint}")
            elif response.status_code == 500:
                log_with_timestamp(f"✅ Endpoint EXISTS (server error): {endpoint}")
            else:
                log_with_timestamp(f"✅ Endpoint EXISTS (status {response.status_code}): {endpoint}")
                
        except Exception as e:
            log_with_timestamp(f"❌ Could not test {endpoint}: {e}")

def main():
    """Main test function"""
    
    log_with_timestamp("🚀 CHINESE API PAYSTATUS WORKFLOW TEST")
    log_with_timestamp("Testing if payStatus is required before orderData")
    log_with_timestamp("=" * 80)
    
    # Check available endpoints first
    check_chinese_api_documentation()
    
    # Test the 3-step workflow
    success = test_paystatus_workflow()
    
    log_with_timestamp(f"\n" + "=" * 80)
    log_with_timestamp("🏁 PAYSTATUS WORKFLOW TEST COMPLETE")
    
    if success:
        log_with_timestamp("✅ 3-step workflow successful!")
    else:
        log_with_timestamp("❌ 3-step workflow failed")
        log_with_timestamp("💡 Possible issues:")
        log_with_timestamp("   - payStatus endpoint missing or incorrect")
        log_with_timestamp("   - Different workflow required")
        log_with_timestamp("   - Chinese API expects different parameters")
        log_with_timestamp("   - Timing still not sufficient")

if __name__ == '__main__':
    main()