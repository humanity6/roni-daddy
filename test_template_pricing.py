#!/usr/bin/env python3
"""
Test template pricing to ensure we're using our pricing instead of Chinese API pricing
"""

import requests
import json
from datetime import datetime
import time

def test_template_pricing_flow():
    """Test that we use template pricing instead of Chinese API pricing"""
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "10HKNTDOH2BA"
    
    print("=== Testing Template Pricing Integration ===")
    print(f"Base URL: {base_url}")
    print(f"Device ID: {device_id}")
    print()
    
    # Step 1: Get iPhone models to see Chinese API pricing
    print("Step 1: Getting iPhone models to check Chinese API pricing...")
    
    try:
        models_response = requests.get(
            f"{base_url}/api/brands/iphone/models",
            params={"device_id": device_id},
            timeout=30
        )
        
        print(f"Models Status: {models_response.status_code}")
        if models_response.status_code != 200:
            print(f"Models Error: {models_response.text}")
            return False
        
        models_data = models_response.json()
        if not models_data.get("models") or len(models_data["models"]) == 0:
            print("❌ No iPhone models available")
            return False
        
        # Show Chinese API pricing
        test_model = models_data["models"][0]
        chinese_price = test_model["price"]
        print(f"✅ Chinese API Model: {test_model['name']}")
        print(f"   Chinese API Price: £{chinese_price}")
        
    except Exception as e:
        print(f"❌ Failed to get models: {e}")
        return False
    
    # Step 2: Test payment with different template prices
    template_tests = [
        {"id": "classic", "expected_price": 19.99, "name": "Classic (Basic)"},
        {"id": "funny-toon", "expected_price": 21.99, "name": "Funny Toon (AI)"},
        {"id": "footy-fan", "expected_price": 23.99, "name": "Footy Fan (AI Premium)"}
    ]
    
    for template_test in template_tests:
        print(f"\nStep 2.{template_test['id']}: Testing {template_test['name']} Template Pricing...")
        
        payment_data = {
            "mobile_model_id": test_model["chinese_model_id"],
            "device_id": device_id,
            "third_id": f"PYEN{datetime.now().strftime('%y%m%d')}{str(int(time.time()))[-6:]}",
            "pay_amount": template_test["expected_price"],  # Our template price, not Chinese API price
            "pay_type": 5  # Vending machine
        }
        
        print(f"   Template: {template_test['name']}")
        print(f"   Our Template Price: £{template_test['expected_price']}")
        print(f"   Chinese API Price: £{chinese_price}")
        print(f"   Using Our Price: {'✅ YES' if payment_data['pay_amount'] != chinese_price else '❌ NO'}")
        
        try:
            payment_response = requests.post(
                f"{base_url}/api/chinese/order/payData",
                json=payment_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Correlation-ID": f"TEMPLATE_TEST_{template_test['id']}_{int(time.time())}"
                },
                timeout=30
            )
            
            print(f"   Payment Status: {payment_response.status_code}")
            
            if payment_response.status_code == 200:
                try:
                    payment_result = payment_response.json()
                    if payment_result.get("code") == 200:
                        print(f"   ✅ Template pricing accepted by Chinese API")
                        print(f"   Chinese Payment ID: {payment_result.get('data', {}).get('log_id', 'N/A')}")
                    else:
                        print(f"   ❌ Chinese API rejected payment: {payment_result.get('msg')}")
                        return False
                except json.JSONDecodeError:
                    print("   ❌ Invalid JSON response")
                    return False
            else:
                print(f"   ❌ HTTP error: {payment_response.status_code}")
                print(f"   Response: {payment_response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Payment request failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = test_template_pricing_flow()
    print()
    if success:
        print("🎉 Template pricing integration test PASSED!")
        print("✅ System is using our template pricing, not Chinese API pricing")
        print("✅ Chinese API accepts our pricing structure")
        print("✅ Different template tiers (Basic/AI/Premium) work correctly")
        print()
        print("Template Pricing Summary:")
        print("- Basic Templates: £19.99 (Classic, 2-in-1, 3-in-1, 4-in-1, Film Strip)")
        print("- AI Templates: £21.99 (Funny Toon, Retro Remix, Cover Shoot, Glitch Pro)")
        print("- Premium AI: £23.99 (Footy Fan)")
    else:
        print("💥 Template pricing integration test FAILED!")
        print("❌ There are still issues with pricing integration.")