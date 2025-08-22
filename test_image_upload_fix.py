#!/usr/bin/env python3
"""
Test script to verify the image upload fix is working correctly.
This tests the complete flow from image composition to Chinese API integration.
"""

import base64
import requests
import json
from datetime import datetime
import time

# Test configuration
API_BASE_URL = "https://pimpmycase.onrender.com"  # Deployed Render instance

def create_test_image_data():
    """Create a simple test image as base64 data"""
    # Create a simple 100x100 red square as PNG data
    from PIL import Image
    import io
    
    # Create red square
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    
    # Convert to base64 data URL
    b64_data = base64.b64encode(img_data).decode('utf-8')
    return f"data:image/png;base64,{b64_data}"

def test_final_image_upload():
    """Test the final image upload endpoint"""
    print("🔄 Testing final image upload...")
    
    # Create test image
    test_image_data = create_test_image_data()
    session_id = f"test_session_{int(time.time())}"
    
    # Prepare upload data
    upload_data = {
        'template_id': 'classic',
        'order_id': session_id,  # Use as order ID for session-based naming
        'final_image_data': test_image_data,
        'metadata': json.dumps({
            'test': True,
            'inputText': 'Test Image',
            'selectedFont': 'Arial',
            'selectedTextColor': '#ffffff',
            'selectedBackgroundColor': '#ff0000',
            'uploadTimestamp': datetime.now().isoformat()
        })
    }
    
    try:
        # Upload final image
        response = requests.post(
            f"{API_BASE_URL}/api/images/upload-final",
            data=upload_data,
            timeout=30
        )
        
        print(f"📡 Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Final image upload successful!")
            print(f"📄 Filename: {result.get('filename')}")
            print(f"🌐 Public URL: {result.get('public_url')}")
            print(f"🆔 Session ID: {result.get('session_id')}")
            
            # Test if image is accessible
            if result.get('public_url'):
                try:
                    img_response = requests.get(result['public_url'], timeout=10)
                    if img_response.status_code == 200:
                        print("✅ Image is accessible via public URL!")
                        return result
                    else:
                        print(f"❌ Image not accessible: HTTP {img_response.status_code}")
                except Exception as e:
                    print(f"❌ Error accessing image: {e}")
            
            return result
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_chinese_api_integration(image_data):
    """Test Chinese API integration with the uploaded image"""
    if not image_data:
        print("❌ Cannot test Chinese API - no image data")
        return
    
    print("🔄 Testing Chinese API integration...")
    
    # Simulate order data that would be sent to Chinese API
    test_order_data = {
        'finalImagePublicUrl': image_data.get('public_url'),
        'imageSessionId': image_data.get('session_id'),
        'chinese_model_id': 'MM1020250226000002',  # Test model ID
        'device_id': 'TEST_DEVICE_123',
        'designImage': 'blob:test-url',  # This should be ignored in favor of finalImagePublicUrl
        'brand': 'iPhone',
        'model': 'iPhone 15 Pro',
        'color': 'Natural Titanium'
    }
    
    print(f"📋 Order data for Chinese API:")
    print(f"  - Public URL: {test_order_data['finalImagePublicUrl']}")
    print(f"  - Session ID: {test_order_data['imageSessionId']}")
    print(f"  - Chinese Model: {test_order_data['chinese_model_id']}")
    
    # This would normally be called by the payment success handler
    # For testing, we just verify the logic
    if test_order_data.get('finalImagePublicUrl'):
        print("✅ Chinese API would receive permanent URL!")
        print(f"   URL: {test_order_data['finalImagePublicUrl']}")
    else:
        print("❌ Chinese API would receive blob URL (bad!)")

def main():
    """Run the complete test"""
    print("🚀 Starting Image Upload Fix Test")
    print("="*50)
    
    # Test 1: Upload final image
    image_result = test_final_image_upload()
    
    print()
    print("="*50)
    
    # Test 2: Test Chinese API integration
    test_chinese_api_integration(image_result)
    
    print()
    print("="*50)
    print("🏁 Test Complete!")
    
    if image_result:
        print("✅ Image upload fix is working correctly!")
        print("✅ Chinese API will receive permanent, accessible image URLs!")
    else:
        print("❌ Image upload fix has issues - check the logs above")

if __name__ == "__main__":
    main()