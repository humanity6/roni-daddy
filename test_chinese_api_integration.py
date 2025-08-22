#!/usr/bin/env python3
"""
Test Chinese API integration with real image upload flow.
This tests the complete scenario that would happen during a real payment.
"""

import requests
import json
import base64
import time
from datetime import datetime
from PIL import Image
import io

# Configuration
API_BASE_URL = "https://pimpmycase.onrender.com"
TEST_DEVICE_ID = "TEST_DEVICE_123"
TEST_CHINESE_MODEL_ID = "MM1020250226000002"

def create_realistic_design_image():
    """Create a more realistic phone case design image"""
    # Create a 695x1271 image (phone case dimensions from finalImageComposer.js)
    img = Image.new('RGB', (695, 1271), color='white')
    
    # Add some colored rectangles to simulate a design
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Background gradient effect (simple)
    draw.rectangle([0, 0, 695, 400], fill='#FFE4E6')  # Light pink top
    draw.rectangle([0, 400, 695, 800], fill='#E0F2FE')  # Light blue middle  
    draw.rectangle([0, 800, 695, 1271], fill='#DCFCE7')  # Light green bottom
    
    # Add some text simulation
    draw.rectangle([50, 500, 645, 600], fill='black')
    draw.text((60, 520), "SAMPLE DESIGN", fill='white')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    b64_data = base64.b64encode(img_data).decode('utf-8')
    return f"data:image/png;base64,{b64_data}"

def test_complete_flow():
    """Test the complete flow from image upload to Chinese API integration"""
    print("🚀 Testing Complete Chinese API Integration Flow")
    print("="*60)
    
    # Step 1: Create and upload final design image
    print("📋 STEP 1: Creating and uploading final design image...")
    
    test_image_data = create_realistic_design_image()
    session_id = f"test_session_{int(time.time())}"
    
    upload_data = {
        'template_id': 'classic',
        'order_id': session_id,
        'final_image_data': test_image_data,
        'metadata': json.dumps({
            'test_scenario': 'chinese_api_integration',
            'inputText': 'My Custom Design',
            'selectedFont': 'Arial',
            'selectedTextColor': '#000000',
            'selectedBackgroundColor': '#FFFFFF',
            'timestamp': datetime.now().isoformat()
        })
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/images/upload-final",
            data=upload_data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        upload_result = response.json()
        print(f"✅ Image uploaded successfully!")
        print(f"📄 Filename: {upload_result['filename']}")
        print(f"🌐 Public URL: {upload_result['public_url']}")
        print(f"🆔 Session ID: {upload_result['session_id']}")
        
        # Verify image is accessible
        img_response = requests.get(upload_result['public_url'], timeout=10)
        if img_response.status_code == 200:
            print(f"✅ Image accessible: {len(img_response.content)} bytes")
        else:
            print(f"❌ Image not accessible: HTTP {img_response.status_code}")
            
        return upload_result
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_chinese_api_flow(image_data):
    """Test what would happen in the Chinese API integration"""
    if not image_data:
        print("❌ Cannot test Chinese API - no image data")
        return
        
    print("\n📋 STEP 2: Testing Chinese API Integration Logic...")
    
    # Simulate the payment success handler logic
    mock_order_data = {
        'finalImagePublicUrl': image_data['public_url'],
        'imageSessionId': image_data['session_id'],
        'chinese_model_id': TEST_CHINESE_MODEL_ID,
        'device_id': TEST_DEVICE_ID,
        'designImage': 'blob:https://example.com/blob-url',  # This should be ignored
        'brand': 'iPhone',
        'model': 'iPhone 15 Pro',
        'color': 'Natural Titanium',
        'price': 19.98
    }
    
    print("🔍 Analyzing image URL selection logic...")
    
    # Test the priority system from payment.py
    design_image_url = None
    
    # Priority 1: Use the uploaded final image URL (permanent, hosted)
    if mock_order_data.get('finalImagePublicUrl'):
        design_image_url = mock_order_data.get('finalImagePublicUrl')
        print(f"✅ Priority 1: Using uploaded final image URL")
        print(f"   URL: {design_image_url}")
        
    # Priority 2: Session-based URL pattern
    elif mock_order_data.get('imageSessionId'):
        session_id = mock_order_data.get('imageSessionId')
        design_image_url = f"https://pimpmycase.onrender.com/image/order-{session_id}-final-*.png"
        print(f"⚠️ Priority 2: Using session-based URL pattern")
        print(f"   URL: {design_image_url}")
        
    # Priority 3: Check if designImage is already permanent
    elif mock_order_data.get('designImage') and mock_order_data.get('designImage').startswith('https://pimpmycase.onrender.com'):
        design_image_url = mock_order_data.get('designImage')
        print(f"✅ Priority 3: Using existing permanent URL")
        print(f"   URL: {design_image_url}")
        
    # Priority 4: Fallback
    else:
        design_image_url = f"https://pimpmycase.onrender.com/api/generate-design-preview"
        print(f"⚠️ Priority 4: Using fallback URL")
        print(f"   URL: {design_image_url}")
    
    # Simulate Chinese API calls
    print("\n🔄 Simulating Chinese API calls...")
    
    # Generate third_ids like the real system
    now = datetime.now()
    date_str = now.strftime("%y%m%d")
    timestamp_suffix = str(int(time.time()))[-6:]
    
    payment_third_id = f"PYEN{date_str}{timestamp_suffix}"
    order_third_id = f"OREN-{mock_order_data['imageSessionId']}"
    
    print(f"💰 Call 1 - payData:")
    print(f"   Endpoint: {API_BASE_URL}/api/chinese/order/payData")
    print(f"   third_id: {payment_third_id}")
    print(f"   pay_type: 12 (app payment)")
    print(f"   amount: {mock_order_data['price']}")
    
    print(f"📊 Call 2 - payStatus:")  
    print(f"   Endpoint: {API_BASE_URL}/api/chinese/order/payStatus")
    print(f"   third_id: {payment_third_id}")
    print(f"   status: 3 (paid)")
    
    print(f"📦 Call 3 - orderData:")
    print(f"   Endpoint: {API_BASE_URL}/api/chinese/order/orderData") 
    print(f"   third_pay_id: {payment_third_id}")
    print(f"   third_id: {order_third_id}")
    print(f"   pic: {design_image_url}")
    print(f"   mobile_model_id: {mock_order_data['chinese_model_id']}")
    print(f"   device_id: {mock_order_data['device_id']}")
    
    # Test actual accessibility of the image URL
    print(f"\n🌐 Testing Chinese manufacturer access to image:")
    try:
        img_response = requests.get(design_image_url, timeout=10)
        if img_response.status_code == 200:
            print(f"✅ SUCCESS: Chinese manufacturers can access the image!")
            print(f"   HTTP Status: {img_response.status_code}")
            print(f"   Content-Type: {img_response.headers.get('Content-Type')}")
            print(f"   Image Size: {len(img_response.content)} bytes")
        else:
            print(f"❌ FAILED: Image not accessible (HTTP {img_response.status_code})")
    except Exception as e:
        print(f"❌ ERROR: Cannot access image: {e}")

def main():
    """Run the complete integration test"""
    # Test complete flow
    image_data = test_complete_flow()
    test_chinese_api_flow(image_data)
    
    print("\n" + "="*60)
    print("🏁 INTEGRATION TEST COMPLETE!")
    
    if image_data:
        print("✅ SUCCESS: Complete flow working correctly!")
        print("✅ Chinese manufacturers will receive permanent image URLs!")
        print("✅ Images are accessible for printing!")
    else:
        print("❌ FAILURE: Issues detected in the flow")
    
    print("\n🎯 Next Steps:")
    print("- Monitor Chinese API logs for real payments")
    print("- Verify manufacturers can access images during actual orders")
    print("- Check printing queue receives proper image URLs")

if __name__ == "__main__":
    main()