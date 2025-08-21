#!/usr/bin/env python3
"""
Debug the models endpoint to understand the response format
"""

import requests
import json

def debug_models_endpoint():
    """Debug the models endpoint response"""
    
    base_url = "https://pimpmycase.onrender.com"
    device_id = "10HKNTDOH2BA"
    
    print("=== Debugging Models Endpoint ===")
    print(f"Base URL: {base_url}")
    print(f"Device ID: {device_id}")
    print()
    
    try:
        response = requests.get(
            f"{base_url}/api/brands/iphone/models",
            params={"device_id": device_id},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Raw Response: {response.text}")
        print()
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON Data Type: {type(data)}")
                print(f"JSON Data: {json.dumps(data, indent=2)}")
                
                if isinstance(data, list):
                    print(f"Number of models: {len(data)}")
                    if len(data) > 0:
                        print(f"First model: {data[0]}")
                elif isinstance(data, dict):
                    print(f"Dict keys: {list(data.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
        else:
            print("❌ Non-200 status code")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    debug_models_endpoint()