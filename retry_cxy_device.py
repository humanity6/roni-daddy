#!/usr/bin/env python3
"""
Retry the CXY device with fresh test - Chinese team says to try again
"""

import sys
import os
import json
from datetime import datetime
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.chinese_payment_service import get_chinese_payment_client

def test_cxy_device_again():
    """Test CXY device again as requested by Chinese team"""
    
    device_id = "CXYLOGD8OQUK"
    
    print("🔄 RETESTING CXY DEVICE AS REQUESTED BY CHINESE TEAM")
    print("=" * 70)
    print(f"Device ID: {device_id}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    client = get_chinese_payment_client()
    
    # Test with fresh authentication
    print("🔑 Step 1: Fresh Authentication")
    try:
        client.token = None  # Force fresh login
        auth_success = client.login()
        if auth_success:
            print(f"✅ Authentication successful")
            print(f"   Token: {client.token[:30]}...")
        else:
            print(f"❌ Authentication failed")
            return
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return
    
    print()
    
    # Test 1: Stock API
    print("📦 Step 2: Testing Stock API")
    try:
        stock_response = client.get_stock_list(device_id=device_id, brand_id="BR20250111000002")
        
        if stock_response.get("success"):
            stock_items = stock_response.get("stock_items", [])
            print(f"✅ Stock API: Found {len(stock_items)} models")
            for i, item in enumerate(stock_items):
                print(f"   {i+1}. {item.get('mobile_model_name')}: {item.get('mobile_model_id')} (Stock: {item.get('stock')})")
        else:
            print(f"❌ Stock API failed: {stock_response.get('message')}")
            return
    except Exception as e:
        print(f"❌ Stock API error: {str(e)}")
        return
    
    print()
    
    # Test 2: Payment API  
    print("💳 Step 3: Testing Payment API")
    test_third_id = f"RETRY{int(datetime.now().timestamp())}"
    
    try:
        payment_response = client.send_payment_data(
            mobile_model_id="MM020250224000010",  # iPhone 15 Pro
            third_id=test_third_id,
            pay_amount=19.99,
            pay_type=5,
            device_id=device_id
        )
        
        if payment_response.get('code') == 200:
            chinese_payment_id = payment_response.get('data', {}).get('id')
            print(f"✅ Payment API: SUCCESS")
            print(f"   Third ID: {test_third_id}")
            print(f"   Chinese Payment ID: {chinese_payment_id}")
            print(f"   Message: {payment_response.get('msg')}")
        else:
            print(f"❌ Payment API failed: {payment_response.get('code')} - {payment_response.get('msg')}")
            return
    except Exception as e:
        print(f"❌ Payment API error: {str(e)}")
        return
    
    print()
    
    # Wait a moment before testing order API
    print("⏱️ Waiting 2 seconds before order test...")
    time.sleep(2)
    
    # Test 3: Order API - THE CRITICAL TEST
    print("📋 Step 4: Testing Order API (CRITICAL TEST)")
    test_order_id = f"RONEN{int(datetime.now().timestamp())}"
    
    try:
        order_response = client.send_order_data(
            third_pay_id=chinese_payment_id,
            third_id=test_order_id,
            mobile_model_id="MM020250224000010",
            pic="https://pimpmycase.onrender.com/logo.png",
            device_id=device_id
        )
        
        print(f"📤 Order API Response:")
        print(f"   Status Code: {order_response.get('code')}")
        print(f"   Message: {order_response.get('msg')}")
        
        if order_response.get('code') == 200:
            print(f"🎉 ORDER API SUCCESS!")
            order_data = order_response.get('data', {})
            print(f"   Order ID: {order_data.get('id', 'N/A')}")
            print(f"   Queue Number: {order_data.get('queue_no', 'N/A')}")
            print(f"   Status: {order_data.get('status', 'N/A')}")
            
            print()
            print("🎉 DEVICE IS FULLY WORKING!")
            print(f"✅ All 3 APIs work: Stock ✅ Payment ✅ Order ✅")
            print(f"✅ Use device ID: {device_id}")
            
            return True
            
        else:
            print(f"❌ Order API still failing:")
            print(f"   Code: {order_response.get('code')}")
            print(f"   Error: {order_response.get('msg')}")
            
            # Show full response for debugging
            print(f"   Full Response: {json.dumps(order_response, indent=2, ensure_ascii=False)}")
            
            return False
            
    except Exception as e:
        print(f"❌ Order API error: {str(e)}")
        return False

def test_different_parameters():
    """Try different parameters to see if that helps"""
    device_id = "CXYLOGD8OQUK" 
    
    print("🧪 TESTING WITH DIFFERENT PARAMETERS")
    print("=" * 50)
    
    client = get_chinese_payment_client()
    
    # Test with different mobile model IDs from the stock
    model_ids_to_test = [
        "MM020250224000010",  # iPhone 15 Pro
        "MM020250224000011",  # iPhone 15 Pro Max  
        "MM1020250226000002", # iPhone 16 Pro Max
    ]
    
    for model_id in model_ids_to_test:
        print(f"📱 Testing with model: {model_id}")
        
        try:
            # Create payment
            test_third_id = f"TEST{model_id[-4:]}{int(datetime.now().timestamp())}"
            payment_response = client.send_payment_data(
                mobile_model_id=model_id,
                third_id=test_third_id,
                pay_amount=19.99,
                pay_type=5,
                device_id=device_id
            )
            
            if payment_response.get('code') == 200:
                chinese_payment_id = payment_response.get('data', {}).get('id')
                print(f"   ✅ Payment: {chinese_payment_id}")
                
                # Try order
                test_order_id = f"ORD{model_id[-4:]}{int(datetime.now().timestamp())}"
                order_response = client.send_order_data(
                    third_pay_id=chinese_payment_id,
                    third_id=test_order_id,
                    mobile_model_id=model_id,
                    pic="https://pimpmycase.onrender.com/logo.png",
                    device_id=device_id
                )
                
                if order_response.get('code') == 200:
                    print(f"   🎉 Order SUCCESS with model {model_id}!")
                    return True
                else:
                    print(f"   ❌ Order failed: {order_response.get('msg')}")
            else:
                print(f"   ❌ Payment failed: {payment_response.get('msg')}")
                
        except Exception as e:
            print(f"   ❌ Error with {model_id}: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🔄 RETESTING CXY DEVICE AS REQUESTED")
    print("🕐 Current time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))
    print()
    
    # Main test
    success = test_cxy_device_again()
    
    if not success:
        print()
        print("🔄 Trying with different model IDs...")
        success = test_different_parameters()
    
    if success:
        print("\n🎉 SOLUTION FOUND!")
        print("✅ Device CXYLOGD8OQUK is working")
        print("✅ Ready to update production system")
    else:
        print("\n⚠️ Still having issues")
        print("❌ Device CXYLOGD8OQUK still cannot process orders")