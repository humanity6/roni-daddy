#!/usr/bin/env python3
"""
Simple script to generate a test link for simulating Chinese vending machine QR code.
This creates a valid URL that mimics what a real vending machine QR code would contain.
"""

import uuid
import urllib.parse
from datetime import datetime

def generate_vending_test_link():
    """Generate a test URL that simulates a Chinese vending machine QR code"""
    
    # Base URL (your frontend domain)
    base_url = "https://pimpmycase.shop"
    
    # Generate a unique session ID (simulating what the vending machine would create)
    session_id = f"VM{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
    
    # Vending machine parameters (simulating Chinese vending machine data)
    vending_params = {
        'qr': '1',  # Indicates this is a QR code scan
        'session_id': session_id,
        'machine_id': 'VMTEST003',  # Use third test machine with proper ID format
        'location': 'Test Location 3 - Mall',
        'currency': 'GBP',
        'vending': 'true',  # Flag to indicate vending machine mode
        'timestamp': str(int(datetime.now().timestamp()))
    }
    
    # Build the complete URL
    query_string = urllib.parse.urlencode(vending_params)
    test_url = f"{base_url}?{query_string}"
    
    return test_url, vending_params

def main():
    """Main function to generate and display the test link"""
    print("Chinese Vending Machine Test Link Generator")
    print("=" * 50)
    
    # Generate the test URL
    test_url, params = generate_vending_test_link()
    
    print("Generated Test URL:")
    print(f"{test_url}")
    print()
    
    print("URL Parameters:")
    for key, value in params.items():
        print(f"   {key}: {value}")
    print()
    
    print("How to use:")
    print("1. Copy the generated URL above")
    print("2. Open it in your browser or mobile device")
    print("3. This will simulate scanning a QR code from a Chinese vending machine")
    print("4. The app should detect vending machine mode and show the appropriate payment flow")
    print()
    
    print("Testing Steps:")
    print("1. Navigate through brand -> model -> template -> upload -> text -> payment")
    print("2. Choose 'Pay via Machine' option")
    print("3. The app should now use real API polling instead of simulation")
    print("4. Monitor the backend API calls to /api/vending/session/{session_id}/status")
    print()
    
    # Save to file option
    save_option = input("Save this URL to a file? (y/n): ").lower().strip()
    if save_option == 'y':
        filename = f"vending_test_link_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(f"Vending Machine Test URL\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"URL: {test_url}\n\n")
            f.write("Parameters:\n")
            for key, value in params.items():
                f.write(f"{key}: {value}\n")
        print(f"URL saved to: {filename}")

if __name__ == "__main__":
    main()