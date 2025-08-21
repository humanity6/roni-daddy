#!/usr/bin/env python3
"""
Simple test for Chinese payment endpoint with proper authentication
URL: http://app-dev.deligp.com:8500/mobileShell/en/order/payData
"""

import requests
import json
import hashlib
import time
from datetime import datetime

def generate_signature(payload, system_name="mobileShell", fixed_key="shfoa3sfwoehnf3290rqefiz4efd"):
    """Generate MD5 signature for Chinese API authentication"""
    parts = []
    
    # Sort all fields by key and add primitive values
    if isinstance(payload, dict):
        for key in sorted(payload.keys()):
            value = payload.get(key)
            if value is not None and isinstance(value, (str, int, float, bool)):
                parts.append(str(value))
    
    # Append system_name and fixed_key
    parts.append(system_name)
    parts.append(fixed_key)
    
    signature_string = "".join(parts)
    return hashlib.md5(signature_string.encode("utf-8")).hexdigest()

def login_and_get_token():
    """Login to get authentication token"""
    login_url = "http://app-dev.deligp.com:8500/mobileShell/en/user/login"
    login_payload = {
        "account": "taharizvi.ai@gmail.com",
        "password": "EN112233"
    }
    
    login_headers = {
        'Content-Type': 'application/json',
        'req_source': 'en',
        'sign': generate_signature(login_payload)
    }
    
    print("Logging in to get token...")
    try:
        response = requests.post(login_url, json=login_payload, headers=login_headers, timeout=30)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                token = data.get("data", {}).get("token")
                if token:
                    print(f"✅ Login successful! Token: {token[:20]}...")
                    return token
                else:
                    print("❌ No token in response")
            else:
                print(f"❌ Login failed: {data.get('msg')}")
        return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_endpoint():
    # First login to get token
    token = login_and_get_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    url = "http://app-dev.deligp.com:8500/mobileShell/en/order/payData"
    
    # Generate third_id following the pattern: PREFIX + yyMMdd + 6 digits
    third_id = f"PYEN{datetime.now().strftime('%y%m%d')}{str(int(time.time()))[-6:]}"
    
    payload = {
        "mobile_model_id": "test_model_123",
        "device_id": "1CBRONIQRWQQ",
        "third_id": third_id,
        "pay_amount": 10.0,
        "pay_type": 1
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'req_source': 'en',
        'sign': generate_signature(payload),
        'Authorization': token
    }
    
    print("Testing Chinese Payment Endpoint")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("\n❌ AUTHENTICATION REQUIRED")
            print("The endpoint is working but requires authentication")
            print("Chinese message translates to: 'Request access failed, authentication failed, unable to access system resources'")
        elif response.status_code == 200:
            print("\n✅ SUCCESS")
        else:
            print(f"\n⚠️  Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint()