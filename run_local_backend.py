#!/usr/bin/env python3
"""
LOCAL BACKEND RUNNER
Runs the FastAPI backend locally for faster testing without render deployments
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

def run_backend():
    """Run the FastAPI backend locally"""
    
    backend_dir = Path(__file__).parent / "backend"
    
    print("🚀 Starting local FastAPI backend...")
    print(f"📁 Backend directory: {backend_dir}")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Run the API server
    try:
        # Use uvicorn to run the FastAPI app
        cmd = [sys.executable, "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        print(f"🔧 Running command: {' '.join(cmd)}")
        
        process = subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Error running backend: {e}")
        print("\n💡 Make sure you have installed the requirements:")
        print("   pip install -r requirements-api.txt")
        print("   pip install uvicorn")

def run_frontend():
    """Run the Vite frontend locally"""
    
    frontend_dir = Path(__file__).parent
    
    print("🚀 Starting local Vite frontend...")
    print(f"📁 Frontend directory: {frontend_dir}")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    try:
        # Run npm run dev
        cmd = ["npm", "run", "dev"]
        print(f"🔧 Running command: {' '.join(cmd)}")
        
        process = subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error running frontend: {e}")
        print("\n💡 Make sure you have installed npm dependencies:")
        print("   npm install")

def main():
    """Main function"""
    
    print("🔧 LOCAL DEVELOPMENT SETUP")
    print("=" * 50)
    
    choice = input("""
What would you like to run?
1. Backend only (FastAPI on port 8000)
2. Frontend only (Vite on port 5173) 
3. Both (backend + frontend)
4. Test Chinese API (with local backend)

Enter choice (1-4): """).strip()
    
    if choice == "1":
        print("\n🔸 Starting Backend Only")
        run_backend()
    elif choice == "2":
        print("\n🔸 Starting Frontend Only")
        run_frontend()
    elif choice == "3":
        print("\n🔸 Starting Both Backend and Frontend")
        
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Wait a bit for backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Start frontend
        run_frontend()
        
    elif choice == "4":
        print("\n🔸 Testing Chinese API with Local Backend")
        
        # Check if backend is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Local backend is running")
            else:
                print("❌ Local backend is not responding correctly")
                return
        except:
            print("❌ Local backend is not running")
            print("💡 Start the backend first with option 1")
            return
        
        # Run tests against localhost
        print("🧪 Running tests against localhost:8000...")
        
        # Create local test script
        test_script = Path(__file__).parent / "test_localhost_chinese_api.py"
        test_content = '''
import requests
import json
import time
from datetime import datetime

def test_localhost():
    base_url = "http://localhost:8000"
    device_id = "CXYLOGD8OQUK"
    
    # Generate proper third_id format: PYEN + yyMMdd + 6digits
    now = datetime.now()
    date_str = now.strftime("%y%m%d")  # yyMMdd format
    timestamp_suffix = str(int(time.time() * 1000))[-6:]
    third_id = f"PYEN{date_str}{timestamp_suffix}"
    
    print(f"🆔 Testing with ID: {third_id}")
    print(f"📅 Date format: {date_str} (yyMMdd)")
    
    # Test payData
    pay_data = {
        "third_id": third_id,
        "pay_amount": 19.99,
        "pay_type": 5,
        "mobile_model_id": "MM1020250226000002",
        "device_id": device_id
    }
    
    print("\\n🔸 Testing payData...")
    try:
        response = requests.post(f"{base_url}/api/chinese/order/payData", json=pay_data, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.ok and response.json().get('code') == 200:
            chinese_payment_id = response.json()['data']['id']
            print(f"✅ PayData success: {third_id} -> {chinese_payment_id}")
            
            # Test orderData
            print("\\n🔸 Testing orderData...")
            order_data = {
                "third_pay_id": third_id,
                "third_id": f"OREN{date_str}{str(int(time.time() * 1000))[-6:]}",
                "mobile_model_id": "MM1020250226000002",
                "pic": "http://localhost:8000/uploads/test-image.jpg",
                "device_id": device_id
            }
            
            order_response = requests.post(f"{base_url}/api/chinese/order/orderData", json=order_data, timeout=45)
            print(f"Status: {order_response.status_code}")
            result = order_response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            debug_info = result.get('_debug', {})
            print(f"\\n🔍 PayStatus attempted: {debug_info.get('pre_pay_status_attempted', False)}")
            print(f"🔍 PayStatus code: {debug_info.get('pay_status_resp_code')}")
            
            if result.get('code') == 200:
                print("✅ SUCCESS: Order created!")
            else:
                print(f"❌ Failed: {result.get('msg')}")
        else:
            print("❌ PayData failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_localhost()
'''
        
        with open(test_script, 'w') as f:
            f.write(test_content)
        
        # Run the test
        subprocess.run([sys.executable, str(test_script)])
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()