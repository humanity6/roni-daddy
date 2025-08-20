#!/usr/bin/env python3
"""
Add test vending machine to database
This script adds the test machine used in generate_test_urls.py to the database
"""

import requests
import json

def add_test_vending_machine():
    """Add the test vending machine 1CBRONIQRWQQ to the database"""
    
    api_base_url = "https://pimpmycase.onrender.com"  # Production API URL
    
    # Machine data matching the one used in generate_test_urls.py
    machine_data = {
        "machine_id": "1CBRONIQRWQQ",
        "name": "Test Vending Machine - Chinese API",
        "location": "Testing Environment - Chinese API Integration",
        "is_active": True,
        "qr_config": {
            "base_url": "https://pimpmycase.shop/",
            "timeout_minutes": 30,
            "language": "en"
        }
    }
    
    print("=" * 80)
    print("🤖 Adding Test Vending Machine to Database")
    print("=" * 80)
    print()
    print(f"Machine ID: {machine_data['machine_id']}")
    print(f"Name: {machine_data['name']}")
    print(f"Location: {machine_data['location']}")
    print(f"API Endpoint: {api_base_url}/api/chinese/machines")
    print()
    
    try:
        print("Sending request to add machine...")
        
        response = requests.post(
            f"{api_base_url}/api/chinese/machines",
            json=machine_data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "PimpMyCase-TestScript/1.0"
            },
            timeout=30
        )
        
        print(f"HTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Test vending machine added successfully!")
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("success"):
                print()
                print("🎉 Machine is now ready for testing!")
                print("You can now use the URLs from generate_test_urls.py")
                
                # Generate a test URL
                from generate_test_urls import generate_test_url
                test_url, session_id = generate_test_url(
                    machine_id="1CBRONIQRWQQ",
                    location="Test Environment"
                )
                print()
                print("📱 Test URL:")
                print(test_url)
                print(f"Session ID: {session_id}")
        else:
            print("❌ FAILED: Could not add vending machine")
            try:
                error_data = response.json()
                print(f"Error Response: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Raw Error Response: {response.text}")
                
        print()
        print("=" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        print()
        print("This might be due to:")
        print("- Network connectivity issues")
        print("- API server being down")
        print("- Invalid API endpoint")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_test_vending_machine()