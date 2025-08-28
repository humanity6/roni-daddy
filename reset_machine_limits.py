#!/usr/bin/env python3
"""Force reset machine session limits"""

import requests
import json

def reset_machine_limits():
    """Force reset in-memory session limits"""
    
    machine_id = "CXYLOGD8OQUK"
    base_url = "https://pimpmycase.onrender.com"
    
    # Try to reset via admin endpoint if available
    try:
        print(f"🔄 Attempting to reset session limits for {machine_id}...")
        
        # Try admin reset endpoint
        response = requests.post(
            f"{base_url}/api/admin/machines/{machine_id}/reset-session-count",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin reset successful: {result}")
            return True
        else:
            print(f"⚠️ Admin endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Admin reset failed: {e}")
    
    # Try creating a test session to see current state
    try:
        print(f"🧪 Testing session creation...")
        
        test_payload = {
            "machine_id": machine_id,
            "location": "Test Reset Session",
            "session_timeout_minutes": 1,  # Very short timeout
            "metadata": {"test": "reset_limits"}
        }
        
        response = requests.post(
            f"{base_url}/api/vending/create-session",
            json=test_payload,
            timeout=10
        )
        
        print(f"Session creation test: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Session creation now works!")
            return True
        elif response.status_code == 429:
            print(f"❌ Still getting 429 - may need backend restart")
            print(f"Response: {response.text}")
        else:
            print(f"⚠️ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    return False

if __name__ == '__main__':
    if reset_machine_limits():
        print("🎉 Machine limits reset successfully!")
    else:
        print("❌ Machine limits reset failed - may need manual intervention")