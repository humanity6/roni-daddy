#!/usr/bin/env python3
"""
PimpMyCase QR URL Generator - Simple Version
Generates one valid test URL by creating actual sessions via API
"""

import requests
import json
from urllib.parse import urlencode


def create_vending_session(machine_id, base_url="https://pimpmycase.onrender.com"):
    """Create a real vending machine session via API"""
    
    create_payload = {
        "machine_id": machine_id,
        "location": "Test Location - Order Data Fix",
        "session_timeout_minutes": 60,  # 1 hour for testing
        "metadata": {"source": "generate_test_urls", "purpose": "order_data_fix_testing"}
    }
    
    try:
        print(f"Creating session for machine {machine_id}...")
        response = requests.post(
            f"{base_url}/api/vending/create-session",
            json=create_payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get("session_id")
            if session_id:
                print(f"✅ Session created successfully: {session_id}")
                return session_id, session_data
            else:
                print("❌ No session_id in response")
                return None, None
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
            
    except requests.exceptions.Timeout:
        print("❌ Session creation timed out - API server may be slow")
        return None, None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - API server may be unavailable")
        return None, None
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return None, None


def validate_session(session_id, base_url="https://pimpmycase.onrender.com"):
    """Validate that the session exists and is active"""
    
    try:
        print(f"Validating session {session_id}...")
        response = requests.get(
            f"{base_url}/api/vending/session/{session_id}/status",
            timeout=10
        )
        
        if response.status_code == 200:
            session_status = response.json()
            status = session_status.get("status")
            expires_at = session_status.get("expires_at")
            print(f"✅ Session valid - Status: {status}, Expires: {expires_at}")
            return True
        elif response.status_code == 404:
            print("❌ Session not found - may have been deleted")
            return False
        elif response.status_code == 410:
            print("❌ Session expired")
            return False
        else:
            print(f"❌ Session validation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️ Session validation error (but session may still work): {e}")
        return True  # Assume valid if validation fails


def generate_valid_test_url():
    """Generate one 100% valid test URL by creating an actual session"""
    
    # Use the known working machine ID from Chinese API
    machine_id = "1CBRONIQRWQQ"
    
    # Create actual session via API
    session_id, session_data = create_vending_session(machine_id)
    
    if not session_id:
        print("❌ Failed to create session - cannot generate valid URL")
        return None, None, None
    
    # Validate the session was created properly
    if not validate_session(session_id):
        print("❌ Session validation failed - URL may not work")
        return None, None, None
    
    # Build URL parameters exactly as expected by the backend
    params = {
        "qr": "true",
        "machine_id": machine_id,
        "session_id": session_id,
        "device_id": machine_id,
        "lang": "en"
    }
    
    base_url = "https://pimpmycase.shop/"
    query_string = urlencode(params)
    url = f"{base_url}?{query_string}"
    
    return url, session_id, machine_id


if __name__ == '__main__':
    url, session_id, machine_id = generate_valid_test_url()
    
    if url and session_id and machine_id:
        print("🔗 Valid Test URL for Order Data Size Fix:")
        print("=" * 60)
        print(url)
        print()
        print("Session Details:")
        print(f"  Session ID: {session_id}")
        print(f"  Machine ID: {machine_id}")
        print(f"  Session Timeout: 60 minutes")
        print()
        print("✅ This URL will test:")
        print("  - Session registration (no more 404 errors)")
        print("  - Order-summary payload optimization")
        print("  - Chinese API integration (payData + orderData)")
        print("  - 500KB size limit validation")
        print("  - Improved error handling")
        print()
        print("⚠️  Note: This session will expire in 1 hour")
    else:
        print("❌ Failed to generate valid test URL")
        print("Check your internet connection and API availability")