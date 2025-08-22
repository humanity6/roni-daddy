#!/usr/bin/env python3
"""
Test different device IDs to find which ones are accepted
"""

import requests
import json
import time

BASE_URL = "https://pimpmycase.onrender.com"

def test_device_id(device_id):
    """Test a specific device ID"""
    test_payload = {
        "mobile_model_id": "MM1020250226000002",
        "device_id": device_id,
        "third_id": f"PYEN{int(time.time() * 1000) % 1000000000000:012d}",
        "pay_amount": 0.01,
        "pay_type": 12
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chinese/order/payData",
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        success = data.get("code") == 200
        message = data.get("msg", "Unknown error")
        chinese_id = data.get('data', {}).get('id', 'N/A') if success else None
        return success, message, chinese_id
    else:
        return False, f"HTTP {response.status_code}", None

def main():
    print("🧪 Testing Different Device IDs")
    print("=" * 50)
    
    # Test various device ID formats
    device_ids_to_test = [
        "APP-PAYMENT",           # Our corrected format
        "APP_PAYMENT",           # Original incorrect format
        "CXYLOGD8OQUK",         # Known vending machine ID
        "1CBRONIQRWQQ",         # Device ID from documentation
        "VM_TEST_MANUFACTURER",  # Test device from API
        "10HKNTDOH2BA",         # Another test device
        "CN_DEBUG_01"           # Debug device
    ]
    
    for device_id in device_ids_to_test:
        print(f"\n🔧 Testing device ID: {device_id}")
        success, message, chinese_id = test_device_id(device_id)
        
        if success:
            print(f"✅ ACCEPTED - Chinese Payment ID: {chinese_id}")
        else:
            print(f"❌ REJECTED - {message}")
    
    print(f"\n" + "=" * 50)
    print("🧪 Testing with Chinese API brands...")
    
    # Test getting stock with different device IDs
    response = requests.get(f"{BASE_URL}/api/chinese/stock/CXYLOGD8OQUK/BR20250111000002")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✅ CXYLOGD8OQUK works for stock API")
        else:
            print(f"❌ CXYLOGD8OQUK failed for stock: {data.get('error')}")
    
    # Test the configured device ID from documentation
    response = requests.get(f"{BASE_URL}/api/chinese/stock/1CBRONIQRWQQ/BR20250111000002")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✅ 1CBRONIQRWQQ works for stock API")
        else:
            print(f"❌ 1CBRONIQRWQQ failed for stock: {data.get('error')}")

if __name__ == "__main__":
    main()