#!/usr/bin/env python3
"""
Debug script to test vending machine registration manually and see detailed errors
"""

import requests
import json
import sys

def test_registration_debug():
    """Test the registration endpoint with detailed debugging"""
    
    base_url = "https://pimpmycase.onrender.com"
    machine_id = "VMTEST003"  # Use third test machine with no underscores
    
    print("Testing Vending Machine Registration Debug")
    print("=" * 50)
    
    # Step 1: Create a session first
    print("Step 1: Creating vending machine session...")
    
    create_payload = {
        "machine_id": machine_id,
        "location": "Test Location 3 - Mall",
        "session_timeout_minutes": 30,
        "metadata": {"source": "debug_test"}
    }
    
    try:
        create_response = requests.post(
            f"{base_url}/api/vending/create-session",
            json=create_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Create Session Status: {create_response.status_code}")
        print(f"Create Session Response: {create_response.text}")
        
        if create_response.status_code != 200:
            print("Session creation failed")
            return
            
        session_data = create_response.json()
        session_id = session_data.get("session_id")
        
        if not session_id:
            print("No session_id in response")
            return
            
        print(f"Session created: {session_id}")
        
    except Exception as e:
        print(f"Session creation error: {e}")
        return
    
    # Step 2: Try to register with the session
    print(f"\nStep 2: Registering user with session {session_id}...")
    
    register_payload = {
        "machine_id": machine_id,
        "session_id": session_id,
        "location": "Test Location 3 - Mall",
        "user_agent": "Debug Test Agent",
        "ip_address": None
    }
    
    try:
        register_response = requests.post(
            f"{base_url}/api/vending/session/{session_id}/register-user",
            json=register_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Registration Status: {register_response.status_code}")
        print(f"Registration Response: {register_response.text}")
        
        if register_response.status_code == 200:
            print("Registration successful!")
            registration_data = register_response.json()
            print(f"Registration Data: {json.dumps(registration_data, indent=2)}")
        else:
            print("Registration failed")
            if register_response.status_code == 400:
                print("This is a 400 Bad Request - likely validation error")
            elif register_response.status_code == 404:
                print("This is a 404 Not Found - session not found")
            elif register_response.status_code == 410:
                print("This is a 410 Gone - session expired")
                
    except Exception as e:
        print(f"Registration error: {e}")
        return
    
    print("\n" + "=" * 50)
    print("Debug test complete")

if __name__ == "__main__":
    test_registration_debug()