#!/usr/bin/env python3
"""
Test script to verify the payment and order fixes are working
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://pimpmycase.onrender.com"

def test_chinese_api_connection():
    """Test if Chinese API connection is working"""
    print("🔧 Testing Chinese API connection...")
    response = requests.get(f"{BASE_URL}/api/chinese/test-connection")
    data = response.json()
    
    if data.get("status") == "success" and data.get("chinese_api_connection", {}).get("status") == "connected":
        print("✅ Chinese API connection successful")
        return True
    else:
        print("❌ Chinese API connection failed")
        print(json.dumps(data, indent=2))
        return False

def test_device_id_format():
    """Test if APP-PAYMENT device ID format is accepted"""
    print("\n🔧 Testing device ID format fix...")
    
    # Test with corrected APP-PAYMENT format
    test_payload = {
        "mobile_model_id": "MM1020250226000002",
        "device_id": "APP-PAYMENT",  # Using corrected format with hyphen
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
        if data.get("code") == 200:
            print("✅ APP-PAYMENT device ID format accepted")
            print(f"   Chinese Payment ID: {data.get('data', {}).get('id', 'N/A')}")
            return test_payload["third_id"], data.get('data', {}).get('id')
        else:
            print(f"❌ Chinese API rejected payment: {data.get('msg')}")
            return None, None
    else:
        print(f"❌ Payment request failed: {response.status_code}")
        print(response.text)
        return None, None

def test_payment_mapping_storage(third_id, chinese_payment_id):
    """Test if payment mapping is stored in database"""
    if not third_id or not chinese_payment_id:
        print("\n⏭️  Skipping payment mapping test (no payment IDs)")
        return False
    
    print(f"\n🔧 Testing payment mapping storage...")
    print(f"   Frontend ID: {third_id}")
    print(f"   Chinese ID: {chinese_payment_id}")
    
    # Wait a moment for database to be updated
    time.sleep(2)
    
    # Check if mapping exists by trying to retrieve it
    response = requests.get(f"{BASE_URL}/api/chinese/payment/{third_id}/status")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data.get("third_id") == third_id:
            print("✅ Payment mapping stored in database successfully")
            return True
        else:
            print("❌ Payment mapping not found in database")
            print(json.dumps(data, indent=2))
            return False
    else:
        print(f"❌ Failed to check payment mapping: {response.status_code}")
        return False

def test_session_validation():
    """Test vending session validation"""
    print("\n🔧 Testing session validation...")
    
    # Test with a properly formatted session ID
    test_session = f"CXYLOGD8OQUK_{datetime.now().strftime('%Y%m%d_%H%M%S')}_TEST123"
    response = requests.get(f"{BASE_URL}/api/chinese/debug/session-validation/{test_session}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("is_valid"):
            print("✅ Session validation working correctly")
            return True
        else:
            print(f"❌ Session validation failed: {data}")
            return False
    else:
        print(f"❌ Session validation endpoint failed: {response.status_code}")
        return False

def test_brands_api():
    """Test brands API with Chinese integration"""
    print("\n🔧 Testing brands API...")
    
    response = requests.get(f"{BASE_URL}/api/brands")
    if response.status_code == 200:
        data = response.json()
        brands = data.get("brands", [])
        
        iphone_brand = next((b for b in brands if b["name"] == "IPHONE"), None)
        if iphone_brand and iphone_brand.get("chinese_brand_id"):
            print("✅ Brands API working with Chinese integration")
            print(f"   iPhone Chinese Brand ID: {iphone_brand['chinese_brand_id']}")
            return True
        else:
            print("❌ Brands API missing Chinese integration")
            return False
    else:
        print(f"❌ Brands API failed: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Payment and Order System Fixes")
    print("=" * 50)
    
    results = []
    
    # Test 1: Chinese API Connection
    results.append(test_chinese_api_connection())
    
    # Test 2: Device ID Format Fix
    third_id, chinese_id = test_device_id_format()
    results.append(third_id is not None and chinese_id is not None)
    
    # Test 3: Payment Mapping Storage
    results.append(test_payment_mapping_storage(third_id, chinese_id))
    
    # Test 4: Session Validation
    results.append(test_session_validation())
    
    # Test 5: Brands API
    results.append(test_brands_api())
    
    # Summary
    print("\n" + "=" * 50)
    print("🧪 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Chinese API Connection",
        "Device ID Format Fix", 
        "Payment Mapping Storage",
        "Session Validation",
        "Brands API Integration"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fixes are working correctly!")
    else:
        print("⚠️  Some issues remain to be addressed.")

if __name__ == "__main__":
    main()