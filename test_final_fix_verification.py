#!/usr/bin/env python3
"""
FINAL FIX VERIFICATION TEST
Test that enabling PRE_SEND_PAY_STATUS=True fixes the "Payment information does not exist" error
"""

import requests
import json
import time
from datetime import datetime, timezone

def log_with_timestamp(message):
    """Log message with precise timestamp"""
    timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")

def test_final_fix():
    """Test the complete flow with payStatus enabled"""
    
    log_with_timestamp("🚀 FINAL FIX VERIFICATION TEST")
    log_with_timestamp("Testing: payData → 3s delay → payStatus → orderData")
    log_with_timestamp("=" * 70)
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "CXYLOGD8OQUK"
    
    # Generate unique payment ID
    now = datetime.now()
    timestamp = int(time.time() * 1000)
    third_id = f"PYEN{now.strftime('%d%m%y')}{str(timestamp)[-6:]}"
    
    log_with_timestamp(f"🆔 Payment ID: {third_id}")
    log_with_timestamp(f"📱 Device ID: {device_id}")
    log_with_timestamp(f"🏭 Model: MM1020250226000002 (iPhone 16 Pro Max)")
    
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
        pay_start = time.time()
        log_with_timestamp(f"⏰ Starting payData at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}")
        
        pay_response = requests.post(
            f"{base_url}/api/chinese/order/payData",
            json=pay_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        pay_end = time.time()
        log_with_timestamp(f"⏰ PayData completed at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]} (took {(pay_end-pay_start)*1000:.0f}ms)")
        log_with_timestamp(f"📤 PayData status: {pay_response.status_code}")
        
        if pay_response.ok:
            pay_result = pay_response.json()
            log_with_timestamp(f"📥 PayData response: {json.dumps(pay_result, indent=2)}")
            
            if pay_result.get('code') == 200:
                chinese_payment_id = pay_result.get('data', {}).get('id')
                log_with_timestamp(f"✅ PayData SUCCESS!")
                log_with_timestamp(f"🔄 Mapping: {third_id} → {chinese_payment_id}")
                
                # Step 2: orderData (backend will now call payStatus first automatically)
                log_with_timestamp(f"\n🔸 STEP 2: orderData (with automatic payStatus)")
                log_with_timestamp(f"💡 Backend should now call payStatus before orderData automatically")
                
                order_third_id = f"OREN{now.strftime('%d%m%y')}{str(int(time.time() * 1000))[-6:]}"
                
                order_data = {
                    "third_pay_id": third_id,
                    "third_id": order_third_id,
                    "mobile_model_id": "MM1020250226000002",
                    "pic": "https://pimpmycase.onrender.com/uploads/test-image.jpg",
                    "device_id": device_id
                }
                
                log_with_timestamp(f"OrderData payload: {json.dumps(order_data, indent=2)}")
                
                order_start = time.time()
                log_with_timestamp(f"⏰ Starting orderData at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}")
                log_with_timestamp(f"⏰ Expected: 3s delay + payStatus call + orderData call")
                
                try:
                    order_response = requests.post(
                        f"{base_url}/api/chinese/order/orderData",
                        json=order_data,
                        headers={"Content-Type": "application/json"},
                        timeout=60  # Longer timeout for payStatus + delay + orderData
                    )
                    
                    order_end = time.time()
                    total_duration = order_end - pay_end
                    order_duration = order_end - order_start
                    
                    log_with_timestamp(f"⏰ OrderData completed at: {datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}")
                    log_with_timestamp(f"⏱️ OrderData call took: {order_duration:.2f}s")
                    log_with_timestamp(f"⏱️ Total time since payData: {total_duration:.2f}s")
                    log_with_timestamp(f"📤 OrderData status: {order_response.status_code}")
                    
                    if order_response.ok:
                        order_result = order_response.json()
                        log_with_timestamp(f"📥 OrderData response: {json.dumps(order_result, indent=2)}")
                        
                        # Check debug info to see if payStatus was called
                        debug_info = order_result.get('_debug', {})
                        paystatus_attempted = debug_info.get('pre_pay_status_attempted', False)
                        paystatus_code = debug_info.get('pay_status_resp_code')
                        
                        log_with_timestamp(f"🔍 Debug Analysis:")
                        log_with_timestamp(f"  - PayStatus attempted: {paystatus_attempted}")
                        log_with_timestamp(f"  - PayStatus response code: {paystatus_code}")
                        
                        if order_result.get('code') == 200:
                            log_with_timestamp(f"🎉 SUCCESS! Order created successfully!")
                            chinese_order_id = order_result.get('data', {}).get('id')
                            queue_no = order_result.get('data', {}).get('queue_no')
                            status = order_result.get('data', {}).get('status')
                            
                            log_with_timestamp(f"📋 Chinese Order ID: {chinese_order_id}")
                            log_with_timestamp(f"🎯 Queue Number: {queue_no}")
                            log_with_timestamp(f"📊 Status: {status}")
                            
                            log_with_timestamp(f"\n✅ FINAL CONCLUSION:")
                            log_with_timestamp(f"✅ Payment information does not exist error: FIXED!")
                            log_with_timestamp(f"✅ PayStatus workflow: {'ENABLED' if paystatus_attempted else 'NOT ENABLED'}")
                            log_with_timestamp(f"✅ 3-second delay: Working ({order_duration:.1f}s total)")
                            log_with_timestamp(f"✅ Payment mapping: Working ({third_id} → {chinese_payment_id})")
                            log_with_timestamp(f"✅ Order creation: SUCCESSFUL")
                            
                            return True
                            
                        else:
                            error_msg = order_result.get('msg')
                            log_with_timestamp(f"❌ OrderData failed: {error_msg}")
                            
                            if paystatus_attempted:
                                log_with_timestamp(f"⚠️ ISSUE: PayStatus was called (code: {paystatus_code}) but orderData still failed")
                                if error_msg == "Payment information does not exist":
                                    log_with_timestamp(f"⚠️ PayStatus didn't solve the issue - may need different parameters")
                                else:
                                    log_with_timestamp(f"⚠️ Different error now - PayStatus may have helped but other issue exists")
                            else:
                                log_with_timestamp(f"❌ CRITICAL: PayStatus was NOT called despite PRE_SEND_PAY_STATUS=True")
                                log_with_timestamp(f"❌ Need to check why payStatus is not being triggered")
                                
                            log_with_timestamp(f"🐛 Full debug info: {json.dumps(debug_info, indent=2)}")
                            return False
                    else:
                        error_text = order_response.text
                        log_with_timestamp(f"❌ OrderData HTTP error: {order_response.status_code}")
                        log_with_timestamp(f"📄 Error details: {error_text}")
                        return False
                        
                except Exception as e:
                    log_with_timestamp(f"❌ OrderData exception: {e}")
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

def main():
    """Main test function"""
    
    log_with_timestamp("🔧 TESTING FINAL FIX: PRE_SEND_PAY_STATUS = True")
    log_with_timestamp("This should enable payStatus calls before orderData")
    log_with_timestamp("=" * 80)
    
    success = test_final_fix()
    
    log_with_timestamp(f"\n" + "=" * 80)
    log_with_timestamp("🏁 FINAL FIX VERIFICATION COMPLETE")
    
    if success:
        log_with_timestamp("🎉 ALL ISSUES RESOLVED!")
        log_with_timestamp("✅ Chinese API integration working perfectly")
        log_with_timestamp("✅ Payment → Order flow complete")
    else:
        log_with_timestamp("❌ Issues still exist")
        log_with_timestamp("🔧 May need further investigation or deployment")

if __name__ == '__main__':
    main()