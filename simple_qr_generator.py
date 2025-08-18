#!/usr/bin/env python3
"""
Simple QR URL Generator for PimpMyCase Vending Machine
Generates QR code URLs without requiring external libraries
"""

import uuid
from datetime import datetime

def generate_session_id(machine_id):
    """Generate a session ID in the format: MACHINE_YYYYMMDD_HHMMSS_RANDOMHEX"""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    random_hex = uuid.uuid4().hex[:8].upper()
    return f"{machine_id}_{date_str}_{time_str}_{random_hex}"

def generate_qr_url(machine_id="CXYLOGD8OQUK", device_id=None, base_url="https://pimpmycase.shop", lang="en"):
    """Generate a QR code URL with proper vending machine parameters"""
    
    # Use machine_id as device_id if not provided separately
    if not device_id:
        device_id = machine_id
    
    # Generate unique session ID
    session_id = generate_session_id(machine_id)
    
    # Build the QR code URL
    qr_url = (
        f"{base_url}/"
        f"?qr=true"
        f"&machine_id={machine_id}"
        f"&session_id={session_id}"
        f"&device_id={device_id}"
        f"&lang={lang}"
    )
    
    return qr_url, session_id

def main():
    print("PimpMyCase QR URL Generator")
    print("=" * 50)
    
    # Generate a few test QR URLs
    test_cases = [
        {
            "name": "London Vending Machine",
            "machine_id": "CXYLOGD8OQUK",
            "base_url": "https://pimpmycase.shop"
        },
        {
            "name": "Test Machine (Local Development)", 
            "machine_id": "DEV001TEST",
            "base_url": "http://localhost:8000"
        },
        {
            "name": "Manchester Machine",
            "machine_id": "MANC2024001", 
            "base_url": "https://pimpmycase.shop"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case #{i}: {test['name']}")
        print("-" * 40)
        
        url, session_id = generate_qr_url(
            machine_id=test["machine_id"],
            base_url=test["base_url"]
        )
        
        print(f"QR Code URL:")
        print(f"   {url}")
        print(f"\nDetails:")
        print(f"   Machine ID: {test['machine_id']}")
        print(f"   Device ID:  {test['machine_id']}")
        print(f"   Session ID: {session_id}")
        print(f"   Base URL:   {test['base_url']}")
        
        # Show what happens when user scans this QR code
        print(f"\nWhen user scans this QR code:")
        print(f"   1. App extracts device_id: {test['machine_id']}")
        print(f"   2. Calls Chinese API with device_id for stock data")
        print(f"   3. Shows available brands (Samsung/Apple/Google)")
        print(f"   4. User selects model with real-time stock info")
        print(f"   5. Payment uses device_id: {test['machine_id']}")
    
    print(f"\nGenerated {len(test_cases)} QR code URLs!")
    print(f"Copy any URL above and paste in browser to test")
    print(f"Make sure your API server is running for local URLs")
    
    # Generate one more custom QR code
    print(f"\nCustom QR Code Generator")
    print("-" * 30)
    
    custom_machine = input("Enter machine ID (or press Enter for default): ").strip()
    if not custom_machine:
        custom_machine = "CUSTOM001"
    
    custom_url, custom_session = generate_qr_url(
        machine_id=custom_machine,
        base_url="https://pimpmycase.shop"
    )
    
    print(f"\nYour Custom QR Code:")
    print(f"   {custom_url}")
    print(f"\nSession ID: {custom_session}")

if __name__ == "__main__":
    main()