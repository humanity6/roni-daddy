#!/usr/bin/env python3
"""
Fix device availability issue - test with different device IDs and find working ones
"""

import sys
import os
import requests
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.chinese_payment_service import get_chinese_payment_client

def test_device_availability():
    """Test different device IDs to find available ones"""
    
    # Test device IDs based on different scenarios
    test_devices = [
        "1CBRONIQRWQQ",  # Current failing device
        "TEST_DEVICE_01",  # Generic test device
        "VM001",  # Simple vending machine ID
        "10HKNTDOH2BA",  # Another ID from logs
        "DEVICE_TEST_01",  # Another test pattern
        "",  # Empty device ID
    ]
    
    client = get_chinese_payment_client()
    
    print("🔍 Testing device availability with Chinese API...")
    print(f"API Base URL: {client.base_url}")
    print(f"Account: {client.account}")
    
    results = {}
    
    for device_id in test_devices:
        print(f"\n🧪 Testing device: '{device_id}'")
        
        try:
            # Test with a simple payment first
            test_payment_response = client.send_payment_data(
                mobile_model_id="MM020250224000010",  # iPhone 15 Pro
                third_id=f"TEST{int(datetime.now().timestamp())}",
                pay_amount=19.99,
                pay_type=5,
                device_id=device_id
            )
            
            print(f"   Payment test result: {test_payment_response.get('code')} - {test_payment_response.get('msg', 'No message')}")
            
            if test_payment_response.get('code') == 200:
                chinese_payment_id = test_payment_response.get('data', {}).get('id')
                print(f"   ✅ Payment successful! Chinese Payment ID: {chinese_payment_id}")
                
                # Now test order data
                test_order_response = client.send_order_data(
                    third_pay_id=chinese_payment_id,
                    third_id=f"OREN{int(datetime.now().timestamp())}",
                    mobile_model_id="MM020250224000010",
                    pic="https://pimpmycase.onrender.com/logo.png",  # Use simple logo for testing
                    device_id=device_id
                )
                
                print(f"   Order test result: {test_order_response.get('code')} - {test_order_response.get('msg', 'No message')}")
                
                results[device_id] = {
                    "payment_success": True,
                    "payment_id": chinese_payment_id,
                    "order_success": test_order_response.get('code') == 200,
                    "order_msg": test_order_response.get('msg'),
                    "status": "✅ WORKING" if test_order_response.get('code') == 200 else "⚠️ PAYMENT_ONLY"
                }
            else:
                results[device_id] = {
                    "payment_success": False,
                    "payment_msg": test_payment_response.get('msg'),
                    "order_success": False,
                    "status": "❌ FAILED"
                }
                
        except Exception as e:
            print(f"   ❌ Error testing device '{device_id}': {str(e)}")
            results[device_id] = {
                "payment_success": False,
                "error": str(e),
                "status": "❌ ERROR"
            }
    
    # Print summary
    print(f"\n📊 DEVICE AVAILABILITY SUMMARY:")
    print("=" * 60)
    
    working_devices = []
    for device_id, result in results.items():
        status = result.get('status', '❌ UNKNOWN')
        print(f"Device '{device_id}': {status}")
        
        if result.get('payment_success') and result.get('order_success'):
            working_devices.append(device_id)
            print(f"  ✅ Payment ID: {result.get('payment_id')}")
            print(f"  ✅ Full workflow successful")
        elif result.get('payment_success'):
            print(f"  ⚠️ Payment works, order fails: {result.get('order_msg', 'Unknown')}")
        else:
            print(f"  ❌ Payment fails: {result.get('payment_msg', result.get('error', 'Unknown'))}")
    
    if working_devices:
        print(f"\n🎉 SOLUTION FOUND!")
        print(f"Working devices: {working_devices}")
        print(f"\nRecommended device ID: '{working_devices[0]}'")
        return working_devices[0]
    else:
        print(f"\n⚠️ NO FULLY WORKING DEVICES FOUND")
        print("Need to contact Chinese team to register device or check API status")
        return None

def test_stock_api():
    """Test stock API to see what devices are actually registered"""
    try:
        print("\n📦 Testing stock API to find registered devices...")
        
        client = get_chinese_payment_client()
        
        # Get Apple brand stock for different devices
        test_devices = ["1CBRONIQRWQQ", "VM001", "TEST_DEVICE", ""]
        
        for device_id in test_devices:
            try:
                stock_response = client.get_stock_list(device_id=device_id, brand_id="BR20250111000002")
                
                if stock_response.get("success"):
                    stock_items = stock_response.get("stock_items", [])
                    print(f"Device '{device_id}': {len(stock_items)} models available")
                    
                    if len(stock_items) > 0:
                        print(f"  ✅ Device has stock! Models: {[item.get('mobile_model_name') for item in stock_items[:3]]}")
                        return device_id
                else:
                    print(f"Device '{device_id}': Failed - {stock_response.get('message')}")
                    
            except Exception as e:
                print(f"Device '{device_id}': Error - {str(e)}")
                
    except Exception as e:
        print(f"Stock API test failed: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 Device Availability Diagnostic Tool")
    print("=" * 50)
    
    # Test stock API first
    working_stock_device = test_stock_api()
    
    # Test payment/order flow
    working_device = test_device_availability()
    
    if working_device:
        print(f"\n✅ RECOMMENDED SOLUTION:")
        print(f"Update device_id from '1CBRONIQRWQQ' to '{working_device}'")
    else:
        print(f"\n⚠️ MANUAL ACTION NEEDED:")
        print(f"Contact Chinese team to:")
        print(f"1. Register device '1CBRONIQRWQQ' in their system")
        print(f"2. Or provide a working device ID")