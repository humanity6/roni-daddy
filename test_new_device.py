#!/usr/bin/env python3
"""
Test the new device ID provided by Chinese team and find device list API
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.chinese_payment_service import get_chinese_payment_client

def test_device_list_api():
    """Try to find the device list API"""
    print("🔍 Searching for device list API...")
    
    client = get_chinese_payment_client()
    
    # Possible device list endpoints
    possible_endpoints = [
        "/device/list",
        "/equipment/list", 
        "/shop/list",
        "/goods/list",
        "/device/roni",
        "/equipment/roni"
    ]
    
    for endpoint in possible_endpoints:
        try:
            print(f"Testing: {client.base_url}{endpoint}")
            
            # Make direct request using the session
            headers = {
                "Authorization": client.token if client.token else "",
                "sign": client.generate_signature({}),
                "req_source": "en",
                "Content-Type": "application/json"
            }
            
            if not client.token:
                client.login()
                headers["Authorization"] = client.token
            
            import requests
            response = requests.post(
                f"{client.base_url}{endpoint}",
                json={},
                headers=headers,
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return data
                
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    return None

def test_new_device_id():
    """Test the new device ID provided by Chinese team"""
    
    new_device_id = "CXYLOGD8OQUK"
    old_device_id = "1CBRONIQRWQQ"
    
    print("🧪 TESTING NEW DEVICE ID FROM CHINESE TEAM")
    print("=" * 60)
    print(f"New Device ID: {new_device_id}")
    print(f"Old Device ID: {old_device_id}")
    print()
    
    client = get_chinese_payment_client()
    
    for device_id in [new_device_id, old_device_id]:
        print(f"📱 Testing Device: {device_id}")
        print("-" * 40)
        
        # Test 1: Stock API
        try:
            stock_response = client.get_stock_list(device_id=device_id, brand_id="BR20250111000002")
            
            if stock_response.get("success"):
                stock_items = stock_response.get("stock_items", [])
                print(f"✅ Stock API: {len(stock_items)} models available")
            else:
                print(f"❌ Stock API: {stock_response.get('message')}")
        except Exception as e:
            print(f"❌ Stock API: Error - {str(e)}")
        
        # Test 2: Payment API
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
                print(f"✅ Payment API: Success - {chinese_payment_id}")
                
                # Test 3: Order API (this is where the old device failed)
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
                        print(f"✅ Order API: SUCCESS! - Device is fully working")
                        order_data = order_response.get('data', {})
                        print(f"   Order ID: {order_data.get('id', 'N/A')}")
                        print(f"   Queue No: {order_data.get('queue_no', 'N/A')}")
                        return device_id  # Return the working device
                    else:
                        print(f"❌ Order API: {order_response.get('code')} - {order_response.get('msg')}")
                        
                except Exception as e:
                    print(f"❌ Order API: Error - {str(e)}")
                    
            else:
                print(f"❌ Payment API: {payment_response.get('code')} - {payment_response.get('msg')}")
                
        except Exception as e:
            print(f"❌ Payment API: Error - {str(e)}")
        
        print()
    
    return None

def test_shops_api():
    """Test the shops API that was mentioned in the api_test_results.json"""
    print("🏪 Testing shops API to find all devices...")
    
    client = get_chinese_payment_client()
    
    try:
        if not client.token:
            client.login()
        
        headers = {
            "Authorization": client.token,
            "sign": client.generate_signature({}),
            "req_source": "en",
            "Content-Type": "application/json"
        }
        
        import requests
        response = requests.post(
            f"{client.base_url}/shop/list",
            json={},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Shops API Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Try to get goods for each shop to find device IDs
            if data.get('code') == 200 and 'data' in data:
                shop_data = data['data']
                if 'list' in shop_data:
                    for shop in shop_data['list']:
                        shop_id = shop.get('id')
                        shop_name = shop.get('name')
                        print(f"\n🏪 Shop: {shop_name} ({shop_id})")
                        
                        # Get goods for this shop
                        try:
                            goods_response = requests.post(
                                f"{client.base_url}/goods/list",
                                json={"shop_id": shop_id},
                                headers=headers,
                                timeout=10
                            )
                            
                            if goods_response.status_code == 200:
                                goods_data = goods_response.json()
                                print(f"   Goods response: {json.dumps(goods_data, indent=2, ensure_ascii=False)}")
                        except Exception as e:
                            print(f"   Error getting goods: {e}")
            
        else:
            print(f"❌ Shops API failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Shops API error: {str(e)}")

if __name__ == "__main__":
    print("🚀 TESTING NEW DEVICE ID FROM CHINESE TEAM")
    print("=" * 80)
    
    # Test the device list APIs
    print("STEP 1: Finding device list API...")
    device_list = test_device_list_api()
    print()
    
    print("STEP 2: Testing shops API...")  
    test_shops_api()
    print()
    
    print("STEP 3: Testing new device ID...")
    working_device = test_new_device_id()
    
    if working_device:
        print("🎉 SUCCESS!")
        print(f"Working device found: {working_device}")
        print(f"\nNext step: Update your system to use device ID '{working_device}' instead of '1CBRONIQRWQQ'")
    else:
        print("⚠️ Still need to find a working device ID")
        print("Check the device list API results above for more device IDs to try")