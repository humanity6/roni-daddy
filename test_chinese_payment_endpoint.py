#!/usr/bin/env python3
"""
Test script for Chinese payment endpoint
URL: http://app-dev.deligp.com:8500/mobileShell/en/order/payData
"""

import requests
import json
import sys
from datetime import datetime

def test_payment_endpoint():
    """Test the Chinese payment endpoint with sample data"""
    
    url = "http://app-dev.deligp.com:8500/mobileShell/en/order/payData"
    
    # Sample payload based on typical payment data structure
    payload = {
        "orderId": "TEST_ORDER_" + str(int(datetime.now().timestamp())),
        "amount": 100,
        "currency": "CNY",
        "paymentMethod": "wechat",
        "userId": "test_user_123",
        "productId": "phone_case_001",
        "deviceId": "vending_machine_001",
        "timestamp": datetime.now().isoformat()
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'PimpMyCase-Test/1.0'
    }
    
    print(f"Testing endpoint: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print("-" * 50)
    
    try:
        # Make the POST request
        response = requests.post(
            url, 
            json=payload, 
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            try:
                json_response = response.json()
                print(f"JSON Response: {json.dumps(json_response, indent=2)}")
            except json.JSONDecodeError:
                print("⚠️  Response is not valid JSON")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout - endpoint may be unreachable")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_with_different_payloads():
    """Test with various payload structures"""
    
    url = "http://app-dev.deligp.com:8500/mobileShell/en/order/payData"
    
    # Test different payload variations
    payloads = [
        # Minimal payload
        {
            "orderId": "MIN_TEST_001",
            "amount": 50
        },
        
        # Extended payload
        {
            "orderId": "EXT_TEST_001", 
            "amount": 150,
            "currency": "CNY",
            "paymentMethod": "alipay",
            "userId": "test_user_456",
            "productId": "phone_case_002",
            "deviceId": "vending_machine_002",
            "timestamp": datetime.now().isoformat(),
            "customerInfo": {
                "phone": "13800138000",
                "email": "test@example.com"
            },
            "productInfo": {
                "name": "Custom Phone Case",
                "description": "AI Generated Phone Case"
            }
        },
        
        # Empty payload
        {}
    ]
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    for i, payload in enumerate(payloads, 1):
        print(f"\n{'='*20} Test {i} {'='*20}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("Chinese Payment Endpoint Test")
    print("=" * 40)
    
    # Run basic test
    test_payment_endpoint()
    
    # Ask if user wants to run extended tests
    print("\n" + "=" * 40)
    extended = input("Run extended tests with different payloads? (y/n): ").lower().strip()
    
    if extended == 'y':
        test_with_different_payloads()
    
    print("\nTest completed.")