#!/usr/bin/env python3
"""
Quick fix to reset the in-memory session counter for testing
"""

import requests
import time

def reset_session_counter():
    """Reset session counter by calling the session creation endpoint with a delay"""
    
    base_url = "https://pimpmycase.onrender.com"
    
    print("Attempting to reset session counter...")
    print("=" * 40)
    
    # Wait a bit for any rate limiting to expire
    print("Waiting 30 seconds for rate limiting to reset...")
    time.sleep(30)
    
    # Try creating a session now
    create_payload = {
        "machine_id": "VM_TEST_001",
        "location": "Test Location",
        "session_timeout_minutes": 30,
        "metadata": {"source": "counter_reset_test"}
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/vending/create-session",
            json=create_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Create Session Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS! Session counter appears to be reset")
            session_data = response.json()
            session_id = session_data.get("session_id")
            print(f"Created session: {session_id}")
            return True
        elif response.status_code == 429:
            print("Still getting 429 - session limit still exceeded")
            return False
        else:
            print(f"Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Request error: {e}")
        return False

if __name__ == "__main__":
    success = reset_session_counter()
    
    if success:
        print("\nYou can now test the vending machine flow!")
    else:
        print("\nStill having issues. The backend may need a restart to reset in-memory counters.")
        print("Alternative: Wait longer or try a different machine_id for testing.")