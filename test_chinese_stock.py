#!/usr/bin/env python3
"""
Chinese API Stock Integration Testing Script

This script tests the complete flow from Chinese API integration to frontend URL generation.
It validates brand/stock fetching, payment processing, and generates test URLs.
"""

import requests
import json
import time
import secrets
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass

# Test configuration - Using values from example Chinese folder
API_BASE_URL = "http://localhost:8000"  # Local FastAPI server for testing
FRONTEND_BASE_URL = "https://pimpmycase.shop"
TEST_DEVICE_ID = "1CBRONIQRWQQ"  # Actual working device ID from fetch_all.py
TEST_MACHINE_ID = "1CBRONIQRWQQ"  # Same as device ID for this test

# Chinese API Configuration (from fetch_all.py)
CHINESE_API_BASE_URL = "http://app-dev.deligp.com:8500/mobileShell/en"
CHINESE_API_ACCOUNT = "taharizvi.ai@gmail.com"
CHINESE_API_PASSWORD = "EN112233"
CHINESE_API_SYSTEM_NAME = "mobileShell"
CHINESE_API_FIXED_KEY = "shfoa3sfwoehnf3290rqefiz4efd"

@dataclass
class TestResult:
    """Test result container"""
    test_name: str
    success: bool
    message: str
    data: Dict[str, Any] = None
    error: str = None

class ChineseAPIIntegrationTester:
    """Comprehensive tester for Chinese API integration"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.session = requests.Session()
        self.session.timeout = 30
    
    def log_result(self, test_name: str, success: bool, message: str, data: Dict[str, Any] = None, error: str = None):
        """Log test result"""
        result = TestResult(test_name, success, message, data, error)
        self.results.append(result)
        
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}: {message}")
        if error:
            print(f"   Error: {error}")
        if data and isinstance(data, dict) and len(str(data)) < 200:
            print(f"   Data: {data}")
    
    def test_chinese_api_connection(self) -> bool:
        """Test connection to Chinese API through our backend"""
        try:
            response = self.session.get(f"{API_BASE_URL}/api/chinese/test-connection")
            
            if response.status_code == 200:
                data = response.json()
                chinese_connection = data.get("chinese_api_connection", {})
                
                if chinese_connection.get("status") == "connected":
                    self.log_result(
                        "Chinese API Connection",
                        True,
                        "Successfully connected to Chinese API",
                        {"base_url": chinese_connection.get("base_url")}
                    )
                    return True
                else:
                    self.log_result(
                        "Chinese API Connection",
                        False,
                        "Chinese API connection failed",
                        error=chinese_connection.get("error")
                    )
                    return False
            else:
                self.log_result(
                    "Chinese API Connection",
                    False,
                    f"Backend connection failed: {response.status_code}",
                    error=response.text
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Chinese API Connection",
                False,
                "Connection test exception",
                error=str(e)
            )
            return False
    
    def test_brand_fetching(self) -> List[Dict[str, Any]]:
        """Test brand fetching from Chinese API"""
        try:
            response = self.session.get(f"{API_BASE_URL}/api/chinese/brands")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    brands = data.get("brands", [])
                    self.log_result(
                        "Brand Fetching",
                        True,
                        f"Fetched {len(brands)} brands successfully",
                        {"total_brands": len(brands), "sample_brand": brands[0] if brands else None}
                    )
                    return brands
                else:
                    self.log_result(
                        "Brand Fetching",
                        False,
                        "Brand fetching failed",
                        error=data.get("error")
                    )
                    return []
            else:
                self.log_result(
                    "Brand Fetching",
                    False,
                    f"Brand request failed: {response.status_code}",
                    error=response.text
                )
                return []
                
        except Exception as e:
            self.log_result(
                "Brand Fetching",
                False,
                "Brand fetching exception",
                error=str(e)
            )
            return []
    
    def test_stock_fetching(self, brands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test stock fetching for available brands"""
        stock_results = {}
        
        for brand in brands:  # Test all brands
            brand_id = brand.get("id")
            brand_name = brand.get("e_name") or brand.get("name")
            is_available = brand.get("available", True)
            
            # Skip unavailable brands for stock testing
            if not is_available:
                self.log_result(
                    f"Stock Fetching - {brand_name}",
                    True,
                    "Brand marked as unavailable, skipping stock check",
                    {"brand_id": brand_id, "available": False}
                )
                continue
            
            try:
                response = self.session.get(f"{API_BASE_URL}/api/chinese/stock/{TEST_DEVICE_ID}/{brand_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        stock_items = data.get("stock_items", [])
                        available_items = data.get("available_items", [])
                        
                        self.log_result(
                            f"Stock Fetching - {brand_name}",
                            True,
                            f"Found {len(available_items)} available models out of {len(stock_items)} total",
                            {
                                "brand_id": brand_id,
                                "total_items": len(stock_items),
                                "available_items": len(available_items)
                            }
                        )
                        
                        stock_results[brand_id] = {
                            "brand_name": brand_name,
                            "stock_items": stock_items,
                            "available_items": available_items
                        }
                    else:
                        self.log_result(
                            f"Stock Fetching - {brand_name}",
                            False,
                            "Stock fetching failed",
                            error=data.get("error")
                        )
                else:
                    self.log_result(
                        f"Stock Fetching - {brand_name}",
                        False,
                        f"Stock request failed: {response.status_code}",
                        error=response.text
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Stock Fetching - {brand_name}",
                    False,
                    "Stock fetching exception",
                    error=str(e)
                )
        
        return stock_results
    
    def test_vending_session_creation(self) -> str:
        """Test vending machine session creation"""
        try:
            payload = {
                "machine_id": TEST_MACHINE_ID,
                "location": "Test Location",
                "session_timeout_minutes": 30,
                "metadata": {"test": True, "created_by": "integration_test"}
            }
            
            response = self.session.post(f"{API_BASE_URL}/api/vending/create-session", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    session_id = data.get("session_id")
                    qr_url = data.get("qr_url")
                    
                    self.log_result(
                        "Vending Session Creation",
                        True,
                        f"Created session: {session_id}",
                        {
                            "session_id": session_id,
                            "qr_url": qr_url,
                            "expires_at": data.get("expires_at")
                        }
                    )
                    return session_id
                else:
                    self.log_result(
                        "Vending Session Creation",
                        False,
                        "Session creation failed",
                        error=data.get("error", "Unknown error")
                    )
                    return None
            else:
                self.log_result(
                    "Vending Session Creation",
                    False,
                    f"Session request failed: {response.status_code}",
                    error=response.text
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Vending Session Creation",
                False,
                "Session creation exception",
                error=str(e)
            )
            return None
    
    def generate_test_urls(self, stock_results: Dict[str, Any]) -> List[str]:
        """Generate test URLs with real stock data"""
        test_urls = []
        
        # Generate timestamp for session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = secrets.token_hex(4).upper()
        session_id = f"{TEST_MACHINE_ID}_{timestamp}_{random_suffix}"
        
        # Create base test URL
        base_url = f"{FRONTEND_BASE_URL}/?qr=true&machine_id={TEST_MACHINE_ID}&session_id={session_id}&device_id={TEST_DEVICE_ID}&lang=en"
        test_urls.append(f"Base Test URL: {base_url}")
        
        # Generate URLs with specific brand/model combinations
        for brand_id, stock_data in stock_results.items():
            brand_name = stock_data["brand_name"]
            available_items = stock_data["available_items"]
            
            if available_items:
                # Create URL with specific brand pre-selected
                brand_url = f"{base_url}&brand_id={brand_id}&brand_name={brand_name}"
                test_urls.append(f"Test with {brand_name}: {brand_url}")
                
                # Create URL with specific model pre-selected
                for item in available_items[:2]:  # First 2 available models
                    model_name = item.get("mobile_model_name")
                    model_id = item.get("mobile_model_id")
                    price = item.get("price")
                    
                    model_url = f"{brand_url}&model_id={model_id}&model_name={model_name}&price={price}"
                    test_urls.append(f"Test {brand_name} {model_name}: {model_url}")
        
        return test_urls
    
    def test_direct_chinese_api(self) -> bool:
        """Test direct connection to Chinese API using credentials from example folder"""
        try:
            # Import the Chinese API client from the example
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), "example Chinese folder temporary"))
            
            from chinese_api import ChineseAPIClient, ChineseAPIConfig
            
            # Use the same config as in fetch_all.py
            config = ChineseAPIConfig(
                base_url=CHINESE_API_BASE_URL,
                system_name=CHINESE_API_SYSTEM_NAME,
                fixed_key=CHINESE_API_FIXED_KEY,
                req_source="en"
            )
            
            client = ChineseAPIClient(
                config=config,
                account=CHINESE_API_ACCOUNT,
                password=CHINESE_API_PASSWORD
            )
            
            # Test login
            login_result = client.login()
            if login_result.get("status") == 200 and login_result.get("data", {}).get("code") == 200:
                self.log_result(
                    "Direct Chinese API Login",
                    True,
                    "Successfully authenticated with Chinese API",
                    {"account": CHINESE_API_ACCOUNT}
                )
                
                # Test brand list
                brand_result = client.brand_list()
                if brand_result.get("status") == 200 and brand_result.get("data", {}).get("code") == 200:
                    brands = brand_result.get("data", {}).get("data", [])
                    self.log_result(
                        "Direct Chinese API Brand List",
                        True,
                        f"Fetched {len(brands)} brands directly from Chinese API",
                        {"total_brands": len(brands)}
                    )
                    
                    # Test stock list for first brand
                    if brands:
                        first_brand = brands[0]
                        brand_id = first_brand.get("id")
                        stock_result = client.stock_list(device_id=TEST_DEVICE_ID, brand_id=brand_id)
                        
                        if stock_result.get("status") == 200 and stock_result.get("data", {}).get("code") == 200:
                            stock_items = stock_result.get("data", {}).get("data", [])
                            available_count = sum(1 for item in stock_items if item.get("stock", 0) > 0)
                            
                            self.log_result(
                                "Direct Chinese API Stock List",
                                True,
                                f"Fetched stock for {first_brand.get('e_name')}: {available_count}/{len(stock_items)} available",
                                {
                                    "brand": first_brand.get('e_name'),
                                    "total_models": len(stock_items),
                                    "available_models": available_count
                                }
                            )
                            return True
                        else:
                            self.log_result(
                                "Direct Chinese API Stock List",
                                False,
                                "Stock list request failed",
                                error=stock_result.get("data", {}).get("msg")
                            )
                    return True
                else:
                    self.log_result(
                        "Direct Chinese API Brand List",
                        False,
                        "Brand list request failed",
                        error=brand_result.get("data", {}).get("msg")
                    )
            else:
                self.log_result(
                    "Direct Chinese API Login",
                    False,
                    "Authentication failed",
                    error=login_result.get("data", {}).get("msg")
                )
                return False
                
        except ImportError as e:
            self.log_result(
                "Direct Chinese API Test",
                False,
                "Cannot import Chinese API client from example folder",
                error=str(e)
            )
            return False
        except Exception as e:
            self.log_result(
                "Direct Chinese API Test",
                False,
                "Direct Chinese API test failed",
                error=str(e)
            )
            return False
        
        return True

    def run_full_integration_test(self) -> bool:
        """Run complete integration test"""
        print("Starting Chinese API Integration Tests")
        print("=" * 80)
        
        # Test 0: Direct Chinese API Test (optional)
        print("\n[INFO] Testing direct Chinese API connection...")
        self.test_direct_chinese_api()
        
        # Test 1: Chinese API Connection through Backend
        print("\n[INFO] Testing Chinese API through our backend...")
        if not self.test_chinese_api_connection():
            print("\n[ERROR] Chinese API connection failed - skipping remaining tests")
            return False
        
        # Test 2: Brand Fetching
        brands = self.test_brand_fetching()
        if not brands:
            print("\n[WARNING] Brand fetching failed - using fallback for remaining tests")
            # Use filtered brand list (iPhone, Samsung, Google)
            brands = [
                {"id": "BR20250111000002", "e_name": "iPhone", "name": "iPhone", "available": True},
                {"id": "BR020250120000001", "e_name": "Samsung", "name": "Samsung", "available": True},
                {"id": "GOOGLE_UNAVAILABLE", "e_name": "Google", "name": "Google", "available": False}
            ]
        
        # Test 3: Stock Fetching
        stock_results = self.test_stock_fetching(brands)
        
        # Test 4: Session Creation
        session_id = self.test_vending_session_creation()
        
        # Test 5: Generate Test URLs
        print("\n[INFO] Generated Test URLs:")
        print("-" * 50)
        test_urls = self.generate_test_urls(stock_results)
        for url in test_urls:
            print(f"   {url}")
        
        # Summary
        print("\n[INFO] Test Summary:")
        print("-" * 50)
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        
        for result in self.results:
            status = "[PASS]" if result.success else "[FAIL]"
            print(f"   {status} {result.test_name}")
        
        print(f"\nResults: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("[SUCCESS] All tests passed! Chinese API integration is working correctly.")
            return True
        else:
            print("[WARNING] Some tests failed. Check the logs above for details.")
            return False

def main():
    """Main test execution"""
    print("Chinese API Stock Integration Testing Script")
    print("=" * 80)
    print(f"Backend API: {API_BASE_URL}")
    print(f"Frontend URLs: {FRONTEND_BASE_URL}")
    print(f"Chinese API: {CHINESE_API_BASE_URL}")
    print(f"Test Device ID: {TEST_DEVICE_ID}")
    print(f"Test Account: {CHINESE_API_ACCOUNT}")
    print("Configuration sourced from: example Chinese folder temporary/fetch_all.py")
    print()
    
    tester = ChineseAPIIntegrationTester()
    success = tester.run_full_integration_test()
    
    print("\n" + "=" * 80)
    if success:
        print("[SUCCESS] Integration test completed successfully!")
        print("The Chinese API integration is ready for production use.")
    else:
        print("[ERROR] Integration test completed with failures.")
        print("Please check the errors above and fix any issues before deployment.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())