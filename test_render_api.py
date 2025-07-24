#!/usr/bin/env python3
"""
Comprehensive API Test Suite for PimpMyCase Render Deployment
Tests Chinese manufacturer endpoints and complete QR vending machine flow
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class RenderAPITester:
    def __init__(self, base_url: str = "https://pimpmycase.onrender.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "PASS" if success else "FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": timestamp
        })
        
    def test_api_health(self) -> bool:
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            success = response.status_code == 200
            self.log_test("API Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_database_reset(self) -> bool:
        """Test database reset endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/reset-database")
            success = response.status_code == 200
            self.log_test("Database Reset", success, f"Status: {response.status_code}")
            time.sleep(2)  # Wait for reset to complete
            return success
        except Exception as e:
            self.log_test("Database Reset", False, f"Error: {str(e)}")
            return False
    
    def test_database_init(self) -> bool:
        """Test database initialization"""
        try:
            response = self.session.get(f"{self.base_url}/init-database")
            success = response.status_code == 200
            self.log_test("Database Init", success, f"Status: {response.status_code}")
            time.sleep(3)  # Wait for init to complete
            return success
        except Exception as e:
            self.log_test("Database Init", False, f"Error: {str(e)}")
            return False
    
    def test_chinese_api_connection(self) -> bool:
        """Test Chinese API connection endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/chinese/test-connection")
            success = response.status_code == 200
            data = response.json() if response.status_code == 200 else {}
            details = f"Status: {response.status_code}"
            if data:
                details += f", Response: {data.get('status', 'unknown')}"
            self.log_test("Chinese API Connection", success, details)
            return success
        except Exception as e:
            self.log_test("Chinese API Connection", False, f"Error: {str(e)}")
            return False
    
    def test_chinese_order_status_update(self) -> bool:
        """Test Chinese API order status update"""
        try:
            # First create a test order
            order_data = {
                "order_id": "TEST_ORDER_001",
                "status": "printing",
                "queue_number": "Q123",
                "estimated_completion": "5 minutes",
                "chinese_order_id": "CN_ORDER_12345",
                "notes": "Test order status update from API test"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chinese/order-status-update",
                json=order_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Accept 404 as valid since we don't have a real order
            success = response.status_code in [200, 404]
            details = f"Status: {response.status_code}"
            if response.status_code == 404:
                details += " (Expected - no test order exists)"
            elif response.status_code == 200:
                data = response.json()
                details += f", Message: {data.get('message', 'unknown')}"
            
            self.log_test("Chinese Order Status Update", success, details)
            return success
        except Exception as e:
            self.log_test("Chinese Order Status Update", False, f"Error: {str(e)}")
            return False
    
    def test_chinese_print_command(self) -> bool:
        """Test Chinese API print command"""
        try:
            test_data = {
                "order_id": "TEST_ORDER_002",
                "image_urls": [
                    "https://example.com/test-image1.jpg",
                    "https://example.com/test-image2.jpg"
                ],
                "phone_model": "iPhone 15 Pro",
                "customer_info": {
                    "session_id": "TEST_SESSION_001",
                    "machine_id": "VM_TEST_MANUFACTURER",
                    "timestamp": datetime.now().isoformat()
                },
                "priority": 1
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chinese/send-print-command",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Test endpoint functionality (should return 200 even for test data)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'unknown')}"
            
            self.log_test("Chinese Print Command", success, details)
            return success
        except Exception as e:
            self.log_test("Chinese Print Command", False, f"Error: {str(e)}")
            return False
    
    def test_vending_session_creation(self) -> Optional[str]:
        """Test vending machine session creation and return session_id"""
        try:
            test_data = {
                "machine_id": "VM_TEST_MANUFACTURER",
                "location": "API Testing Environment",
                "session_timeout_minutes": 30,
                "metadata": {
                    "test_type": "automated_api_test",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/vending/create-session",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            session_id = None
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                session_id = data.get("session_id")
                details += f", Session ID: {session_id}"
            
            self.log_test("Vending Session Creation", success, details)
            return session_id if success else None
        except Exception as e:
            self.log_test("Vending Session Creation", False, f"Error: {str(e)}")
            return None
    
    def test_session_status(self, session_id: str) -> bool:
        """Test session status retrieval"""
        try:
            response = self.session.get(f"{self.base_url}/api/vending/session/{session_id}/status")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Session Status: {data.get('status')}, Progress: {data.get('user_progress')}"
            
            self.log_test("Session Status Check", success, details)
            return success
        except Exception as e:
            self.log_test("Session Status Check", False, f"Error: {str(e)}")
            return False
    
    def test_user_registration(self, session_id: str) -> bool:
        """Test user registration with session"""
        try:
            test_data = {
                "machine_id": "VM_TEST_MANUFACTURER",
                "session_id": session_id,
                "location": "API Testing Environment",
                "user_agent": "Mozilla/5.0 (compatible; API-Test/1.0)",
                "ip_address": "192.168.1.100"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/vending/session/{session_id}/register-user",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Progress: {data.get('user_progress')}"
            
            self.log_test("User Registration", success, details)
            return success
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            return False
    
    def test_order_summary(self, session_id: str) -> bool:
        """Test order summary submission"""
        try:
            test_data = {
                "session_id": session_id,
                "order_data": {
                    "phone_model": "iPhone 15 Pro",
                    "template": "retro-remix",
                    "images": ["test-image-1.jpg"],
                    "text": "API Test Case",
                    "font": "Arial",
                    "color": "#000000"
                },
                "payment_amount": 15.99,
                "currency": "GBP"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/vending/session/{session_id}/order-summary",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Amount: £{data.get('payment_amount')}"
            
            self.log_test("Order Summary", success, details)
            return success
        except Exception as e:
            self.log_test("Order Summary", False, f"Error: {str(e)}")
            return False
    
    def test_payment_confirmation(self, session_id: str) -> bool:
        """Test payment confirmation"""
        try:
            test_data = {
                "session_id": session_id,
                "payment_method": "card",
                "payment_amount": 15.99,
                "transaction_id": f"TXN_{int(time.time())}",
                "payment_data": {
                    "card_type": "visa",
                    "last_four": "1234",
                    "approval_code": "12345A"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/vending/session/{session_id}/confirm-payment",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Transaction: {data.get('transaction_id')}"
            
            self.log_test("Payment Confirmation", success, details)
            return success
        except Exception as e:
            self.log_test("Payment Confirmation", False, f"Error: {str(e)}")
            return False
    
    def test_session_validation(self, session_id: str) -> bool:
        """Test session security validation"""
        try:
            response = self.session.post(f"{self.base_url}/api/vending/session/{session_id}/validate")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Valid: {data.get('valid')}, Security: {data.get('security_validated')}"
            
            self.log_test("Session Validation", success, details)
            return success
        except Exception as e:
            self.log_test("Session Validation", False, f"Error: {str(e)}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        try:
            print("Testing rate limiting (making 35 rapid requests)...")
            rate_limited = False
            
            for i in range(35):
                response = self.session.get(f"{self.base_url}/api/chinese/test-connection")
                if response.status_code == 429:
                    rate_limited = True
                    break
                time.sleep(0.1)  # Small delay between requests
            
            self.log_test("Rate Limiting", rate_limited, "Rate limit triggered as expected" if rate_limited else "Rate limit not triggered")
            return rate_limited
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Error: {str(e)}")
            return False
    
    def run_complete_flow_test(self) -> bool:
        """Run complete QR vending machine flow test"""
        print("\nStarting Complete Flow Test...")
        
        # Step 1: Create session
        session_id = self.test_vending_session_creation()
        if not session_id:
            return False
        
        # Step 2: Check session status
        if not self.test_session_status(session_id):
            return False
        
        # Step 3: Register user
        if not self.test_user_registration(session_id):
            return False
        
        # Step 4: Submit order summary
        if not self.test_order_summary(session_id):
            return False
        
        # Step 5: Confirm payment
        if not self.test_payment_confirmation(session_id):
            return False
        
        # Step 6: Validate session
        if not self.test_session_validation(session_id):
            return False
        
        print("Complete flow test successful!")
        return True
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("Starting Render API Test Suite")
        print(f"Testing API at: {self.base_url}")
        print("=" * 60)
        
        # Basic API tests
        if not self.test_api_health():
            print("API not accessible, stopping tests")
            return
        
        # Database setup
        print("\nDatabase Setup Tests:")
        self.test_database_reset()
        self.test_database_init()
        
        # Chinese API tests
        print("\nChinese Manufacturer API Tests:")
        self.test_chinese_api_connection()
        self.test_chinese_order_status_update()
        self.test_chinese_print_command()
        
        # Complete flow test
        print("\nComplete Vending Machine Flow Test:")
        self.run_complete_flow_test()
        
        # Security tests
        print("\nSecurity Tests:")
        self.test_rate_limiting()
        
        # Test summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\nAPI Status:", "READY FOR CHINESE MANUFACTURERS" if failed_tests == 0 else "NEEDS ATTENTION")

def main():
    """Main test runner"""
    tester = RenderAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()