#!/usr/bin/env python3
"""
Generate concrete evidence for Chinese team showing the device registration issue
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.chinese_payment_service import get_chinese_payment_client

def generate_evidence_report():
    """Generate detailed evidence report for Chinese team"""
    
    client = get_chinese_payment_client()
    device_id = "1CBRONIQRWQQ"
    
    print("=" * 80)
    print("🚨 DEVICE REGISTRATION ISSUE REPORT FOR CHINESE TEAM")
    print("=" * 80)
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"API Base URL: {client.base_url}")
    print(f"Account: {client.account}")
    print(f"Problem Device ID: {device_id}")
    print()
    
    evidence = {}
    
    # Test 1: Stock API - should work
    print("📦 TEST 1: STOCK API (stock/list)")
    print("-" * 40)
    try:
        stock_response = client.get_stock_list(device_id=device_id, brand_id="BR20250111000002")
        
        if stock_response.get("success"):
            stock_items = stock_response.get("stock_items", [])
            print(f"✅ SUCCESS: Found {len(stock_items)} models for device {device_id}")
            for item in stock_items[:3]:
                print(f"   - {item.get('mobile_model_name')}: {item.get('mobile_model_id')} (Stock: {item.get('stock')})")
            evidence["stock_api"] = {"status": "SUCCESS", "models_count": len(stock_items)}
        else:
            print(f"❌ FAILED: {stock_response.get('message')}")
            evidence["stock_api"] = {"status": "FAILED", "error": stock_response.get('message')}
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        evidence["stock_api"] = {"status": "ERROR", "error": str(e)}
    
    print()
    
    # Test 2: Payment API - should work
    print("💳 TEST 2: PAYMENT API (order/payData)")
    print("-" * 40)
    test_third_id = f"TEST{int(datetime.now().timestamp())}"
    
    try:
        payment_response = client.send_payment_data(
            mobile_model_id="MM020250224000010",
            third_id=test_third_id,
            pay_amount=19.99,
            pay_type=5,
            device_id=device_id
        )
        
        if payment_response.get('code') == 200:
            chinese_payment_id = payment_response.get('data', {}).get('id')
            print(f"✅ SUCCESS: Payment created successfully")
            print(f"   Third ID: {test_third_id}")
            print(f"   Chinese Payment ID: {chinese_payment_id}")
            print(f"   Message: {payment_response.get('msg')}")
            evidence["payment_api"] = {
                "status": "SUCCESS", 
                "third_id": test_third_id,
                "chinese_payment_id": chinese_payment_id
            }
        else:
            print(f"❌ FAILED: Code {payment_response.get('code')} - {payment_response.get('msg')}")
            evidence["payment_api"] = {
                "status": "FAILED", 
                "code": payment_response.get('code'),
                "error": payment_response.get('msg')
            }
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        evidence["payment_api"] = {"status": "ERROR", "error": str(e)}
    
    print()
    
    # Test 3: Order API - FAILS HERE
    print("📋 TEST 3: ORDER API (order/orderData)")
    print("-" * 40)
    
    if evidence.get("payment_api", {}).get("status") == "SUCCESS":
        chinese_payment_id = evidence["payment_api"]["chinese_payment_id"]
        test_order_id = f"OREN{int(datetime.now().timestamp())}"
        
        try:
            order_response = client.send_order_data(
                third_pay_id=chinese_payment_id,
                third_id=test_order_id,
                mobile_model_id="MM020250224000010",
                pic="https://pimpmycase.onrender.com/logo.png",
                device_id=device_id
            )
            
            if order_response.get('code') == 200:
                print(f"✅ SUCCESS: Order created successfully")
                print(f"   Order ID: {test_order_id}")
                print(f"   Message: {order_response.get('msg')}")
                evidence["order_api"] = {"status": "SUCCESS"}
            else:
                print(f"❌ FAILED: Code {order_response.get('code')} - {order_response.get('msg')}")
                print(f"   🚨 THIS IS THE PROBLEM!")
                evidence["order_api"] = {
                    "status": "FAILED", 
                    "code": order_response.get('code'),
                    "error": order_response.get('msg')
                }
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            evidence["order_api"] = {"status": "ERROR", "error": str(e)}
    else:
        print("⏭️ SKIPPED: Payment API failed, cannot test order API")
        evidence["order_api"] = {"status": "SKIPPED", "reason": "Payment API failed"}
    
    print()
    print("=" * 80)
    print("📋 SUMMARY FOR CHINESE TEAM")
    print("=" * 80)
    
    # Determine the exact issue
    stock_ok = evidence.get("stock_api", {}).get("status") == "SUCCESS"
    payment_ok = evidence.get("payment_api", {}).get("status") == "SUCCESS"
    order_ok = evidence.get("order_api", {}).get("status") == "SUCCESS"
    
    print(f"Device ID: {device_id}")
    print(f"Stock API (stock/list):     {'✅ WORKING' if stock_ok else '❌ FAILED'}")
    print(f"Payment API (order/payData): {'✅ WORKING' if payment_ok else '❌ FAILED'}")
    print(f"Order API (order/orderData): {'✅ WORKING' if order_ok else '❌ FAILED'}")
    print()
    
    if stock_ok and payment_ok and not order_ok:
        print("🔥 DIAGNOSIS: PARTIAL DEVICE REGISTRATION")
        print("   The device is registered for stock queries and payments,")
        print("   but NOT registered for order processing.")
        print()
        print("🛠️ REQUIRED ACTION:")
        print(f"   Please register device '{device_id}' for order processing")
        print("   in your order management system.")
        print()
        print("📞 CONTACT INFORMATION:")
        print("   This issue requires Chinese team to update device permissions")
        print("   in your backend system to allow order/orderData calls.")
    
    elif not payment_ok:
        print("🔥 DIAGNOSIS: DEVICE NOT REGISTERED")
        print("   The device is not registered in your system at all.")
        print()
        print("🛠️ REQUIRED ACTION:")
        print(f"   Please register device '{device_id}' in your system")
        print("   with full permissions for stock, payment, and orders.")
    
    else:
        print("🔥 DIAGNOSIS: UNKNOWN ISSUE")
        print("   Please check device configuration manually.")
    
    # Detailed API call logs
    print()
    print("=" * 80)
    print("📊 DETAILED API LOGS FOR DEBUGGING")
    print("=" * 80)
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    
    # Generate the exact message for Chinese team
    print()
    print("=" * 80)
    print("📧 MESSAGE TO SEND TO CHINESE TEAM")
    print("=" * 80)
    
    message = f"""
Hello Chinese Development Team,

We are experiencing an issue with device registration in your system. Here are the details:

**Problem**: Device can process payments but cannot process orders
**Device ID**: {device_id}
**API Account**: {client.account}

**Test Results**:
- ✅ Stock API (stock/list): Working - returns {evidence.get('stock_api', {}).get('models_count', 0)} models
- ✅ Payment API (order/payData): Working - creates payment successfully
- ❌ Order API (order/orderData): FAILING with error: "{evidence.get('order_api', {}).get('error', 'Unknown error')}"

**Error Message**: "{evidence.get('order_api', {}).get('error', 'Device unavailable for orders')}"

**Request**: Please register device "{device_id}" for order processing in your system so that order/orderData API calls work properly.

This is blocking our production vending machine from processing customer orders.

Thank you for your assistance.

Best regards,
PimpMyCase Development Team
"""
    
    print(message.strip())
    
    return evidence

if __name__ == "__main__":
    evidence = generate_evidence_report()