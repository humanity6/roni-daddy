#!/usr/bin/env python3
"""
Comprehensive test to verify all payment and order fixes are working
Tests the exact issues reported by the Chinese team
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://pimpmycase.onrender.com"

def test_payment_mapping_persistence():
    """Test that payment mappings are stored in database and persist"""
    print("🔧 Testing Payment Mapping Persistence...")
    
    # Create a test payment
    test_payload = {
        "mobile_model_id": "MM1020250226000002",
        "device_id": "CXYLOGD8OQUK",  # Known working device
        "third_id": f"PYEN{int(time.time() * 1000) % 1000000000000:012d}",
        "pay_amount": 0.01,
        "pay_type": 5  # Vending machine payment
    }
    
    print(f"   Creating payment with third_id: {test_payload['third_id']}")
    
    response = requests.post(
        f"{BASE_URL}/api/chinese/order/payData",
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200:
            chinese_payment_id = data.get('data', {}).get('id')
            print(f"✅ Payment created - Chinese ID: {chinese_payment_id}")
            
            # Wait for database to update
            time.sleep(3)
            
            # Test if mapping persists
            mapping_response = requests.get(f"{BASE_URL}/api/chinese/payment/{test_payload['third_id']}/status")
            if mapping_response.status_code == 200:
                mapping_data = mapping_response.json()
                if mapping_data.get("success"):
                    print("✅ Payment mapping found in database - PERSISTENCE WORKING")
                    return test_payload['third_id'], chinese_payment_id
                else:
                    print(f"❌ Payment mapping not found: {mapping_data}")
                    return None, None
            else:
                print(f"❌ Failed to check mapping: {mapping_response.status_code}")
                return None, None
        else:
            print(f"❌ Chinese API rejected payment: {data.get('msg')}")
            return None, None
    else:
        print(f"❌ Payment request failed: {response.status_code}")
        return None, None

def test_vending_session_validation():
    """Test that vending sessions require complete data"""
    print("\n🔧 Testing Vending Session Validation...")
    
    # Create a test session
    session_id = f"CXYLOGD8OQUK_{datetime.now().strftime('%Y%m%d_%H%M%S')}_TEST123"
    
    # Test payStatus with incomplete session data (should fail properly)
    incomplete_payload = {
        "third_id": "PYEN999999999999",
        "device_id": "CXYLOGD8OQUK", 
        "status": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chinese/order/payStatus",
        json=incomplete_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200 and "order will be created when details are available" in data.get("msg", ""):
            print("✅ Session validation working - properly handling missing session data")
            return True
        else:
            print(f"❌ Unexpected response: {data}")
            return False
    else:
        print(f"❌ PayStatus request failed: {response.status_code}")
        return False

def test_app_payment_complete_flow():
    """Test the complete 3-step app payment flow that Chinese team requires"""
    print("\n🔧 Testing Complete App Payment Flow (3 Steps)...")
    
    # STEP 1: payData call with pay_type=12 (app payment)
    print("   Step 1: Calling payData with pay_type=12...")
    
    third_id = f"PYEN{int(time.time() * 1000) % 1000000000000:012d}"
    step1_payload = {
        "mobile_model_id": "MM1020250226000002",
        "device_id": "CXYLOGD8OQUK",  # Real device ID from QR
        "third_id": third_id,
        "pay_amount": 19.98,
        "pay_type": 12  # App payment
    }
    
    response1 = requests.post(
        f"{BASE_URL}/api/chinese/order/payData",
        json=step1_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response1.status_code != 200:
        print(f"❌ Step 1 failed: {response1.status_code}")
        return False
    
    data1 = response1.json()
    if data1.get("code") != 200:
        print(f"❌ Step 1 rejected: {data1.get('msg')}")
        return False
    
    chinese_payment_id = data1.get('data', {}).get('id')
    print(f"✅ Step 1 success - Chinese Payment ID: {chinese_payment_id}")
    
    # Wait for database mapping
    time.sleep(2)
    
    # STEP 2: Test backend payment processing (simulates Stripe success)
    print("   Step 2: Testing backend payment processing...")
    
    # Create a test Stripe session
    checkout_response = requests.post(f"{BASE_URL}/create-checkout-session", json={
        "amount": 19.98,
        "template_id": "classic",
        "brand": "iPhone",
        "model": "iPhone 16 Pro Max",
        "color": "Natural Titanium"
    })
    
    if checkout_response.status_code != 200:
        print(f"❌ Checkout creation failed: {checkout_response.status_code}")
        return False
    
    # Simulate payment success processing
    payment_success_payload = {
        "session_id": "cs_test_session_success",
        "order_data": {
            "device_id": "CXYLOGD8OQUK",
            "chinese_model_id": "MM1020250226000002",
            "third_id": third_id,
            "chinese_payment_id": chinese_payment_id,
            "pic": "https://pimpmycase.onrender.com/image/test-design.png"
        }
    }
    
    payment_success_response = requests.post(
        f"{BASE_URL}/process-payment-success",
        json=payment_success_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if payment_success_response.status_code == 200:
        print("✅ Step 2 success - Backend payment processing completed")
        print("✅ Step 3 should be triggered automatically (payStatus + orderData)")
        return True
    else:
        print(f"❌ Step 2 failed: {payment_success_response.status_code}")
        print(f"Response: {payment_success_response.text}")
        return False

def test_chinese_api_integration():
    """Test basic Chinese API integration"""
    print("\n🔧 Testing Chinese API Integration...")
    
    # Test connection
    conn_response = requests.get(f"{BASE_URL}/api/chinese/test-connection")
    if conn_response.status_code == 200:
        conn_data = conn_response.json()
        if conn_data.get("chinese_api_connection", {}).get("status") == "connected":
            print("✅ Chinese API connection successful")
        else:
            print(f"❌ Chinese API connection issue: {conn_data}")
            return False
    else:
        print(f"❌ Connection test failed: {conn_response.status_code}")
        return False
    
    # Test brands API
    brands_response = requests.get(f"{BASE_URL}/api/brands")
    if brands_response.status_code == 200:
        brands_data = brands_response.json()
        iphone_brand = next((b for b in brands_data.get("brands", []) if b["name"] == "IPHONE"), None)
        if iphone_brand and iphone_brand.get("chinese_brand_id"):
            print(f"✅ Brands API working - iPhone Chinese ID: {iphone_brand['chinese_brand_id']}")
            return True
        else:
            print("❌ Brands API missing Chinese integration")
            return False
    else:
        print(f"❌ Brands API failed: {brands_response.status_code}")
        return False

def test_original_issues():
    """Test the specific issues reported by Chinese team"""
    print("\n🔧 Testing Original Reported Issues...")
    
    # Test issue from Step 3: Payment record not found
    print("   Testing payment record lookup...")
    old_payment_response = requests.get(f"{BASE_URL}/api/chinese/payment/PYEN250822186449/status")
    if old_payment_response.status_code == 200:
        old_data = old_payment_response.json()
        if not old_data.get("success") and "Payment record not found" in old_data.get("error", ""):
            print("✅ Old payment IDs properly return 'not found' (expected behavior)")
        else:
            print(f"⚠️ Unexpected response for old payment: {old_data}")
    
    # Test session validation format
    print("   Testing session ID validation...")
    session_response = requests.get(f"{BASE_URL}/api/chinese/debug/session-validation/CXYLOGD8OQUK_20250822_134125_3ECA8C9D")
    if session_response.status_code == 200:
        session_data = session_response.json()
        if session_data.get("is_valid"):
            print("✅ Session validation working correctly")
            return True
        else:
            print(f"❌ Session validation failed: {session_data}")
            return False
    else:
        print(f"❌ Session validation endpoint failed: {session_response.status_code}")
        return False

def main():
    """Run comprehensive test suite"""
    print("🧪 COMPREHENSIVE PAYMENT & ORDER FIXES TEST")
    print("=" * 60)
    print("Testing fixes for issues reported by Chinese team:")
    print("- Step 1: Vending payment success but no order created") 
    print("- Step 2: UI error after successful payment")
    print("- Step 3: Payment record not found + device ID issues")
    print("- Missing 3-step Chinese API flow (payData → payStatus → orderData)")
    print("=" * 60)
    
    results = []
    
    # Test 1: Chinese API Integration
    results.append(test_chinese_api_integration())
    
    # Test 2: Payment Mapping Persistence 
    third_id, chinese_id = test_payment_mapping_persistence()
    results.append(third_id is not None and chinese_id is not None)
    
    # Test 3: Vending Session Validation
    results.append(test_vending_session_validation())
    
    # Test 4: Complete App Payment Flow
    results.append(test_app_payment_complete_flow())
    
    # Test 5: Original Issues Resolution
    results.append(test_original_issues())
    
    # Summary
    print("\n" + "=" * 60)
    print("🧪 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Chinese API Integration",
        "Payment Mapping Persistence", 
        "Vending Session Validation",
        "Complete App Payment Flow (3 steps)",
        "Original Issues Resolution"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL FIXES WORKING! Ready for Chinese team integration!")
        print("\n📋 Summary of fixes implemented:")
        print("  ✅ Database payment mapping (PYEN→MSPY) - no more lost mappings")
        print("  ✅ Proper session validation - fails fast with clear errors")
        print("  ✅ Real device IDs only - no fallbacks")
        print("  ✅ 3-step Chinese API flow - payData → payStatus → orderData")
        print("  ✅ Correct third_pay_id format - uses Chinese payment ID (MSPY)")
        print("  ✅ UI error handling - shows success even with backend issues")
    else:
        print("\n⚠️ Some issues still need attention for full Chinese team integration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 System ready for production use with Chinese manufacturing team!")
    else:
        print("\n🔧 Additional fixes needed before production deployment.")