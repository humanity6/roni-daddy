#!/usr/bin/env python3
"""
Test script to verify API server connectivity and endpoints
"""
import requests
import json

API_BASE_URL = 'http://localhost:8000'  # Changed to localhost for better reliability

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Health Check Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"API Status: {data.get('status', 'unknown')}")
            print(f"OpenAI Status: {data.get('openai', 'unknown')}")
            if 'api_key_preview' in data:
                print(f"API Key Preview: {data['api_key_preview']}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Connection Error: {e}")
        return False

def test_styles_endpoint():
    """Test the styles endpoint for each template"""
    templates = ['funny-toon', 'retro-remix', 'cover-shoot', 'glitch-pro', 'footy-fan']
    
    for template in templates:
        try:
            response = requests.get(f"{API_BASE_URL}/styles/{template}")
            print(f"\n{template.upper()} Styles:")
            if response.status_code == 200:
                data = response.json()
                print(f"  Available options: {list(data.values())[0] if data else 'None'}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"  Connection Error: {e}")

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Root Endpoint Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data.get('message', 'No message')}")
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Connection Error: {e}")
        return False

def main():
    print("=" * 50)
    print("API SERVER CONNECTION TEST")
    print("=" * 50)
    print(f"Testing API at: {API_BASE_URL}")
    print()
    
    # Test root endpoint
    print("1. Testing Root Endpoint...")
    root_ok = test_root_endpoint()
    print()
    
    # Test health endpoint
    print("2. Testing Health Endpoint...")
    health_ok = test_health_endpoint()
    print()
    
    # Test styles endpoints
    print("3. Testing Styles Endpoints...")
    test_styles_endpoint()
    print()
    
    # Summary
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    if root_ok and health_ok:
        print("✅ API Server is running and accessible")
        print("✅ All basic endpoints are working")
        print("\nNext steps:")
        print("1. Make sure your OpenAI API key is properly configured")
        print("2. Test image generation from the frontend")
        print("3. Check the console logs for any errors")
    else:
        print("❌ API Server connection issues detected")
        print("\nTroubleshooting:")
        print("1. Make sure the API server is running: python api_server.py")
        print("2. Check if the server is running on the correct port (8000)")
        print("3. Verify your network connection")
        print("4. Check if the API_BASE_URL in the script matches your server")

if __name__ == "__main__":
    main() 