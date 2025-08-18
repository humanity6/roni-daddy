#!/usr/bin/env python3
"""
Simple test script to generate QR codes for PimpMyCase
Run this to quickly generate test QR codes
"""

from generate_qr_code import generate_qr_url, create_qr_code
from datetime import datetime

def main():
    print("🚀 Quick QR Code Generation Test")
    print("=" * 40)
    
    # Test different machine configurations
    test_machines = [
        {
            "name": "London Machine #1",
            "machine_id": "CXYLOGD8OQUK", 
            "device_id": "CXYLOGD8OQUK"
        },
        {
            "name": "Manchester Machine #2", 
            "machine_id": "MANC2024TEST",
            "device_id": "MANC2024TEST"
        },
        {
            "name": "Test Development Machine",
            "machine_id": "DEV001TEST",
            "device_id": "DEV001TEST" 
        }
    ]
    
    for i, machine in enumerate(test_machines, 1):
        print(f"\n📱 {machine['name']}")
        print("-" * 30)
        
        # Generate QR URL
        url, session_id = generate_qr_url(
            machine_id=machine["machine_id"],
            device_id=machine["device_id"],
            base_url="https://pimpmycase.shop",  # Production URL
            lang="en"
        )
        
        print(f"🔗 URL: {url}")
        print(f"🆔 Session: {session_id}")
        
        # For testing locally, also generate localhost version
        local_url, _ = generate_qr_url(
            machine_id=machine["machine_id"],
            device_id=machine["device_id"], 
            base_url="http://localhost:8000",  # Local development
            lang="en"
        )
        
        print(f"🏠 Local: {local_url}")
        
        # Generate QR code image (optional - requires qrcode library)
        try:
            filename = f"test_qr_{machine['machine_id'].lower()}.png"
            saved_file = create_qr_code(url, filename, size=8)
            print(f"💾 QR saved: {saved_file}")
        except ImportError:
            print("💡 Install 'qrcode[pil]' to generate QR images")
        except Exception as e:
            print(f"⚠️  Could not save QR: {e}")
    
    print(f"\n✅ Test complete! Try scanning the QR codes or paste URLs in browser")
    print(f"📝 Note: Make sure your API server is running for local testing")

if __name__ == "__main__":
    main()