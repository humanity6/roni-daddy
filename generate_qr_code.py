#!/usr/bin/env python3
"""
QR Code Generator for PimpMyCase Vending Machine
Generates QR codes with proper session parameters for testing
"""

import qrcode
import uuid
from datetime import datetime
import argparse
import os

def generate_session_id(machine_id):
    """Generate a session ID in the format: MACHINE_YYYYMMDD_HHMMSS_RANDOMHEX"""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    random_hex = uuid.uuid4().hex[:8].upper()
    return f"{machine_id}_{date_str}_{time_str}_{random_hex}"

def generate_qr_url(machine_id=None, device_id=None, base_url="https://pimpmycase.shop", lang="en"):
    """Generate a QR code URL with proper vending machine parameters"""
    
    # Use default machine ID if not provided
    if not machine_id:
        machine_id = "CXYLOGD8OQUK"
    
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

def create_qr_code(url, filename=None, size=10, border=4):
    """Create and save QR code image"""
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR Code
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    
    # Add data to QR code
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qr_code_{timestamp}.png"
    
    qr_image.save(filename)
    return filename

def main():
    parser = argparse.ArgumentParser(description="Generate QR codes for PimpMyCase vending machines")
    parser.add_argument("--machine-id", "-m", help="Machine ID (default: CXYLOGD8OQUK)")
    parser.add_argument("--device-id", "-d", help="Device ID for Chinese API (defaults to machine ID)")
    parser.add_argument("--base-url", "-u", default="https://pimpmycase.shop", 
                       help="Base URL (default: https://pimpmycase.shop)")
    parser.add_argument("--lang", "-l", default="en", help="Language (default: en)")
    parser.add_argument("--output", "-o", help="Output filename for QR code image")
    parser.add_argument("--size", "-s", type=int, default=10, help="QR code box size (default: 10)")
    parser.add_argument("--no-image", action="store_true", help="Don't generate image, just print URL")
    parser.add_argument("--count", "-c", type=int, default=1, help="Number of QR codes to generate")
    
    args = parser.parse_args()
    
    print("🔧 PimpMyCase QR Code Generator")
    print("=" * 50)
    
    # Generate multiple QR codes if requested
    for i in range(args.count):
        # Generate the QR URL
        url, session_id = generate_qr_url(
            machine_id=args.machine_id,
            device_id=args.device_id,
            base_url=args.base_url,
            lang=args.lang
        )
        
        if args.count > 1:
            print(f"\n📱 QR Code #{i+1}")
            print("-" * 20)
        
        print(f"QR Code URL:")
        print(f"   {url}")
        print(f"\n📋 Session Details:")
        print(f"   Machine ID: {args.machine_id or 'CXYLOGD8OQUK'}")
        print(f"   Device ID:  {args.device_id or args.machine_id or 'CXYLOGD8OQUK'}")
        print(f"   Session ID: {session_id}")
        print(f"   Language:   {args.lang}")
        
        # Generate QR code image unless disabled
        if not args.no_image:
            try:
                if args.count > 1:
                    filename = f"qr_code_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                else:
                    filename = args.output
                
                saved_file = create_qr_code(url, filename, args.size)
                print(f"QR Code saved as: {saved_file}")
                print(f"   File size: {os.path.getsize(saved_file)} bytes")
                
            except ImportError:
                print("Could not generate QR code image. Install qrcode library:")
                print("   pip install qrcode[pil]")
            except Exception as e:
                print(f"Error generating QR code: {e}")
        
        print(f"Test URL in browser:")
        print(f"   {url}")
    
    print(f"\n✅ Generated {args.count} QR code(s) successfully!")

if __name__ == "__main__":
    main()