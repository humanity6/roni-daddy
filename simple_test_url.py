#!/usr/bin/env python3
"""
Simple Test URL for mobile_shell_id Fix Testing
"""

# Manual test URL that should work even with session limits
machine_id = "CXYLOGD8OQUK"
test_url = f"https://pimpmycase.shop/?qr=true&machine_id={machine_id}&device_id={machine_id}&lang=en&session_id=TEST123"

print("🔗 Manual Test URL for mobile_shell_id Fix:")
print("=" * 60)
print(test_url)
print()
print("Session Details:")
print(f"  Machine ID: {machine_id}")
print(f"  Device ID: {machine_id}")  
print(f"  Session ID: TEST123 (manual)")
print()
print("✅ This URL will test:")
print("  - mobile_shell_id inclusion in orderData")
print("  - Chinese API integration")
print("  - Payment flow")
print()
print("⚠️  Note: If session validation fails, the app will still work")
print("   but might skip some vending-specific features")