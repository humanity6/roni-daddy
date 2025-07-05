import requests
import hashlib
import json
import logging
import os
from pprint import pformat
from typing import Dict, Any, Optional

# Configure logging for detailed debug output
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class APITester:
    def __init__(self):
        # === CONFIGURATION ===
        self.base_url = "http://app-dev.deligp.com:8500/mobileShell/en"
        self.account = "taharizvi.ai@gmail.com"
        self.password = "EN112233"
        self.system_name = "mobileShell"
        self.fixed_key = "shfoa3sfwoehnf3290rqefiz4efd"
        self.token = None
        self.test_device_id = "TEST_DEVICE_001"  # Default test device ID
        
        # Test results tracking
        self.test_results = {}
        
    def generate_signature(self, payload: Dict[str, Any]) -> str:
        """Generate MD5 signature according to API documentation rules"""
        # Sort all fields alphabetically by key
        sorted_items = sorted(payload.items())
        
        # Concatenate all values
        value_string = ""
        for key, value in sorted_items:
            if value is not None:
                value_string += str(value)
        
        # Add system name and fixed key
        raw_string = value_string + self.system_name + self.fixed_key
        
        # Generate MD5 hash
        sign = hashlib.md5(raw_string.encode('utf-8')).hexdigest()
        
        logging.debug(f"Signature generation:")
        logging.debug(f"  Sorted payload: {dict(sorted_items)}")
        logging.debug(f"  Value string: {value_string}")
        logging.debug(f"  Raw string: {raw_string}")
        logging.debug(f"  Generated sign: {sign}")
        
        return sign
    
    def make_request(self, endpoint: str, payload: Dict[str, Any], use_token: bool = False) -> requests.Response:
        """Make API request with proper headers and signature"""
        url = f"{self.base_url}/{endpoint}"
        
        # Generate signature
        sign = self.generate_signature(payload)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "req_source": "en",
            "sign": sign
        }
        
        # Add authorization token if required
        if use_token and self.token:
            headers["Authorization"] = self.token
        
        # Log request details
        logging.debug(f"Request URL: {url}")
        logging.debug(f"Request headers:\n{pformat(headers)}")
        
        # Mask sensitive information in logs
        masked_payload = {**payload}
        if "password" in masked_payload:
            masked_payload["password"] = "***"
        logging.debug(f"Request payload:\n{pformat(masked_payload)}")
        
        # Make request
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # Log response details
            logging.debug(f"Response status code: {response.status_code}")
            logging.debug(f"Response headers:\n{pformat(dict(response.headers))}")
            
            try:
                logging.debug(f"Response JSON:\n{pformat(response.json())}")
            except ValueError:
                logging.debug(f"Response text:\n{response.text}")
                
            return response
            
        except requests.RequestException as e:
            logging.error(f"HTTP request failed: {e}")
            raise
    
    def test_login(self) -> bool:
        """Test user login endpoint"""
        print("\n🔍 Testing Login...")
        
        payload = {
            "account": self.account,
            "password": self.password
        }
        
        try:
            response = self.make_request("user/login", payload)
            
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 200:
                    self.token = res_json["data"]["token"]
                    print("✅ Login successful!")
                    print(f"   User ID: {res_json['data']['id']}")
                    print(f"   Account: {res_json['data']['account']}")
                    print(f"   Token: {self.token[:50]}...")
                    self.test_results["login"] = {"status": "success", "data": res_json["data"]}
                    return True
                else:
                    print(f"❌ Login failed. Message: {res_json.get('msg')}")
                    self.test_results["login"] = {"status": "failed", "message": res_json.get('msg')}
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(response.text)
                self.test_results["login"] = {"status": "error", "http_code": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ Login test failed with exception: {e}")
            self.test_results["login"] = {"status": "exception", "error": str(e)}
            return False
    
    def test_brand_list(self) -> bool:
        """Test brand list endpoint"""
        print("\n🔍 Testing Brand List...")
        
        payload = {}
        
        try:
            response = self.make_request("brand/list", payload, use_token=True)
            
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 200:
                    brands = res_json.get("data", [])
                    print(f"✅ Brand list retrieved successfully! Found {len(brands)} brands:")
                    for brand in brands:
                        print(f"   - {brand.get('name')} ({brand.get('e_name')}) - ID: {brand.get('id')}")
                    self.test_results["brand_list"] = {"status": "success", "data": brands}
                    return True
                else:
                    print(f"❌ Brand list failed. Message: {res_json.get('msg')}")
                    self.test_results["brand_list"] = {"status": "failed", "message": res_json.get('msg')}
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                self.test_results["brand_list"] = {"status": "error", "http_code": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ Brand list test failed with exception: {e}")
            self.test_results["brand_list"] = {"status": "exception", "error": str(e)}
            return False
    
    def test_stock_list(self, brand_id: Optional[str] = None) -> bool:
        """Test stock list endpoint"""
        print("\n🔍 Testing Stock List...")
        
        # Use brand_id from previous test if available
        if not brand_id and "brand_list" in self.test_results:
            brand_data = self.test_results["brand_list"].get("data", [])
            if brand_data:
                brand_id = brand_data[0].get("id")
                print(f"   Using brand_id from previous test: {brand_id}")
        
        if not brand_id:
            print("❌ No brand_id available for stock test")
            self.test_results["stock_list"] = {"status": "skipped", "reason": "no_brand_id"}
            return False
        
        payload = {
            "device_id": self.test_device_id,
            "brand_id": brand_id
        }
        
        try:
            response = self.make_request("stock/list", payload, use_token=True)
            
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 200:
                    stocks = res_json.get("data", [])
                    print(f"✅ Stock list retrieved successfully! Found {len(stocks)} models:")
                    for stock in stocks:
                        print(f"   - {stock.get('mobile_model_name')} - ID: {stock.get('mobile_model_id')}")
                        print(f"     Price: ${stock.get('price')}, Stock: {stock.get('stock')}")
                    self.test_results["stock_list"] = {"status": "success", "data": stocks}
                    return True
                else:
                    print(f"❌ Stock list failed. Message: {res_json.get('msg')}")
                    self.test_results["stock_list"] = {"status": "failed", "message": res_json.get('msg')}
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                self.test_results["stock_list"] = {"status": "error", "http_code": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ Stock list test failed with exception: {e}")
            self.test_results["stock_list"] = {"status": "exception", "error": str(e)}
            return False
    
    def test_printing_list(self) -> bool:
        """Test printing list endpoint"""
        print("\n🔍 Testing Printing List...")
        
        payload = {
            "device_id": self.test_device_id
        }
        
        try:
            response = self.make_request("order/printList", payload, use_token=True)
            
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 200:
                    orders = res_json.get("data", [])
                    print(f"✅ Printing list retrieved successfully! Found {len(orders)} orders:")
                    for order in orders:
                        print(f"   - {order.get('mobile_model_name')} - Order ID: {order.get('id')}")
                        print(f"     Third ID: {order.get('third_id')}, Queue: {order.get('queue_no')}")
                        print(f"     Status: {order.get('status')}")
                    self.test_results["printing_list"] = {"status": "success", "data": orders}
                    return True
                else:
                    print(f"❌ Printing list failed. Message: {res_json.get('msg')}")
                    self.test_results["printing_list"] = {"status": "failed", "message": res_json.get('msg')}
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                self.test_results["printing_list"] = {"status": "error", "http_code": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ Printing list test failed with exception: {e}")
            self.test_results["printing_list"] = {"status": "exception", "error": str(e)}
            return False
    
    def test_file_upload(self) -> bool:
        """Test file upload endpoint"""
        print("\n🔍 Testing File Upload...")
        
        # Create a simple test file
        test_file_content = "This is a test file for API testing."
        test_file_path = "test_upload.txt"
        
        try:
            # Create test file
            with open(test_file_path, "w") as f:
                f.write(test_file_content)
            
            # Note: File upload typically uses multipart/form-data, not JSON
            # The signature generation might be different for file uploads
            # This is a basic attempt - may need adjustment based on actual API behavior
            
            url = f"{self.base_url}/file/upload"
            
            # For file uploads, we typically don't use JSON payload signature
            # Instead, we might sign the form data parameters
            form_data = {"type": "23"}  # British pictures type
            sign = self.generate_signature(form_data)
            
            headers = {
                "req_source": "en",
                "sign": sign
            }
            
            if self.token:
                headers["Authorization"] = self.token
            
            files = {"file": open(test_file_path, "rb")}
            data = {"type": "23"}
            
            logging.debug(f"File upload URL: {url}")
            logging.debug(f"File upload headers: {pformat(headers)}")
            logging.debug(f"File upload data: {pformat(data)}")
            
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            
            # Close file handle
            files["file"].close()
            
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 200:
                    file_url = res_json.get("data")
                    print(f"✅ File upload successful!")
                    print(f"   File URL: {file_url}")
                    self.test_results["file_upload"] = {"status": "success", "file_url": file_url}
                    return True
                else:
                    print(f"❌ File upload failed. Message: {res_json.get('msg')}")
                    self.test_results["file_upload"] = {"status": "failed", "message": res_json.get('msg')}
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(response.text)
                self.test_results["file_upload"] = {"status": "error", "http_code": response.status_code}
                return False
                
        except Exception as e:
            print(f"❌ File upload test failed with exception: {e}")
            self.test_results["file_upload"] = {"status": "exception", "error": str(e)}
            return False
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Full API Test Suite")
        print("=" * 50)
        
        # Test 1: Login (required for other tests)
        login_success = self.test_login()
        if not login_success:
            print("\n❌ Login failed - skipping remaining tests")
            return
        
        # Test 2: Brand List
        self.test_brand_list()
        
        # Test 3: Stock List (depends on brand list)
        self.test_stock_list()
        
        # Test 4: Printing List
        self.test_printing_list()
        
        # Test 5: File Upload
        self.test_file_upload()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print a summary of all test results"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        for test_name, result in self.test_results.items():
            status = result.get("status", "unknown")
            if status == "success":
                print(f"✅ {test_name.upper()}: SUCCESS")
            elif status == "failed":
                print(f"❌ {test_name.upper()}: FAILED - {result.get('message', 'Unknown error')}")
            elif status == "error":
                print(f"❌ {test_name.upper()}: HTTP ERROR - {result.get('http_code', 'Unknown')}")
            elif status == "exception":
                print(f"❌ {test_name.upper()}: EXCEPTION - {result.get('error', 'Unknown')}")
            elif status == "skipped":
                print(f"⏭️  {test_name.upper()}: SKIPPED - {result.get('reason', 'Unknown')}")
        
        # Calculate success rate
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results.values() if r.get("status") == "success")
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📈 Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")


def main():
    """Main function to run the API tests"""
    tester = APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main() 