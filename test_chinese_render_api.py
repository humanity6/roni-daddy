#!/usr/bin/env python3
"""
Chinese API Testing Suite for Render Deployment
Tests all Chinese manufacturer endpoints against https://pimpmycase.onrender.com

This file simulates the exact API calls Chinese developers were making
and demonstrates both correct and incorrect usage patterns.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys

class ChineseAPITester:
    def __init__(self, base_url: str = "https://pimpmycase.onrender.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ChineseAPITester/1.0.0 (API Integration Testing)'
        })
        self.test_results = []

    def log_test(self, test_name: str, success: bool, details: str, category: str = "API"):
        """Log test results with detailed information"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'category': category,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"[{category}] {status} {test_name}: {details}")

    def test_connection(self) -> bool:
        """Test basic API connectivity"""
        print("\n🔗 Testing API Connection...")
        try:
            response = self.session.get(f"{self.base_url}/api/chinese/test-connection", timeout=30)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Version: {data.get('api_version')}, Machine IDs: {len(data.get('available_machine_ids', []))}"
                print(f"📋 Available Machine IDs: {data.get('available_machine_ids', [])}")
                print(f"🔒 Security Level: {data.get('security_level')}")
                print(f"⚡ Rate Limit: {data.get('debug_info', {}).get('rate_limit')}")
            else:
                details = f"HTTP {response.status_code}: {response.text[:200]}"
            
            self.log_test("API Connection", success, details, "CONNECTION")
            return success
        except Exception as e:
            self.log_test("API Connection", False, f"Connection error: {str(e)}", "CONNECTION")
            return False

    def test_session_validation_correct(self) -> bool:
        """Test session ID validation with CORRECT formats"""
        print("\n✅ Testing CORRECT Session ID Formats...")
        
        correct_session_ids = [
            "10HKNTDOH2BA_20250729_143022_A1B2C3",
            "VM_TEST_MANUFACTURER_20250729_173422_XYZ789", 
            "CN_DEBUG_01_20250730_093542_DEF456",
            "VM001_20250729_143022_ABC123"
        ]
        
        all_passed = True
        for session_id in correct_session_ids:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/chinese/debug/session-validation/{session_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid = data.get('is_valid', False)
                    
                    if is_valid:
                        self.log_test(f"Valid Session ID: {session_id}", True, "Format validated successfully", "VALIDATION")
                    else:
                        self.log_test(f"Valid Session ID: {session_id}", False, f"Unexpected validation failure: {data.get('suggestions', [])}", "VALIDATION")
                        all_passed = False
                else:
                    self.log_test(f"Valid Session ID: {session_id}", False, f"HTTP {response.status_code}", "VALIDATION")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Valid Session ID: {session_id}", False, f"Error: {str(e)}", "VALIDATION")
                all_passed = False
        
        return all_passed

    def test_session_validation_incorrect(self) -> bool:
        """Test session ID validation with INCORRECT formats (showing Chinese mistakes)"""
        print("\n❌ Testing INCORRECT Session ID Formats (Chinese Developer Mistakes)...")
        
        # These are the actual mistakes Chinese developers were making
        incorrect_session_ids = [
            ("10HKNTDOH2BA_2025729_093542_A1B2C3", "Missing leading zero in date (2025729 instead of 20250729)"),
            ("VM001_20250123_143022_A1B2C3?qr=true&machine_id=VM001", "Including URL parameters in session ID"),
            ("vm001_20250729_143022_abc123", "Using lowercase instead of uppercase"),
            ("10HKNTDOH2BA_20250729_1430_A1B2C3", "Incorrect time format (1430 instead of 143000)"),
            ("10HKNTDOH2BA-20250729-143022-A1B2C3", "Using hyphens instead of underscores"),
            ("20250729_143022_A1B2C3", "Missing machine ID"),
            ("10HKNTDOH2BA_20250729_143022", "Missing random part")
        ]
        
        all_detected = True
        for session_id, mistake_description in incorrect_session_ids:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/chinese/debug/session-validation/{session_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid = data.get('is_valid', True)  # Should be False
                    
                    if not is_valid:
                        self.log_test(f"Invalid Session ID Detection", True, f"✅ Correctly detected: {mistake_description}", "VALIDATION")
                        print(f"  💡 Suggestions: {data.get('suggestions', [])}")
                    else:
                        self.log_test(f"Invalid Session ID Detection", False, f"❌ Failed to detect: {mistake_description}", "VALIDATION")
                        all_detected = False
                else:
                    self.log_test(f"Invalid Session ID Detection", False, f"HTTP {response.status_code}", "VALIDATION")
                    all_detected = False
                    
            except Exception as e:
                self.log_test(f"Invalid Session ID Detection", False, f"Error: {str(e)}", "VALIDATION")
                all_detected = False
        
        return all_detected

    def test_vending_session_status_correct(self) -> bool:
        """Test vending session status with correct session IDs"""
        print("\n🎯 Testing Vending Session Status (Correct Format)...")
        
        correct_session_id = "10HKNTDOH2BA_20250729_143022_A1B2C3"
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/vending/session/{correct_session_id}/status",
                timeout=10
            )
            
            # This might return 404 if session doesn't exist, but should not return 400 (bad format)
            if response.status_code == 404:
                self.log_test("Vending Session Status (Correct)", True, "Session not found (expected), but format was accepted", "VENDING")
                return True
            elif response.status_code == 200:
                data = response.json()
                self.log_test("Vending Session Status (Correct)", True, f"Session found: {data.get('status', 'unknown')}", "VENDING")
                return True
            elif response.status_code == 400:
                self.log_test("Vending Session Status (Correct)", False, f"Format rejected: {response.text}", "VENDING")
                return False
            else:
                self.log_test("Vending Session Status (Correct)", False, f"HTTP {response.status_code}: {response.text[:200]}", "VENDING")
                return False
                
        except Exception as e:
            self.log_test("Vending Session Status (Correct)", False, f"Error: {str(e)}", "VENDING")
            return False

    def test_vending_session_status_incorrect(self) -> bool:
        """Test vending session status with incorrect session IDs (reproducing Chinese mistakes)"""
        print("\n🚫 Testing Vending Session Status (Reproducing Chinese Mistakes)...")
        
        # These are the exact session IDs from the render logs that were failing
        incorrect_sessions = [
            "10HKNTDOH2BA_2025729_093542_A1B2C3",  # From the logs - missing zero in date
            "VM001_20250123_143022_A1B2C3?qr=true&machine_id=VM001&session_id=VM001_20250123_143022_A1B2C3&location=mall_level2"  # From logs - with query params
        ]
        
        all_rejected = True
        for session_id in incorrect_sessions:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/vending/session/{session_id}/status",
                    timeout=10
                )
                
                if response.status_code == 400:
                    self.log_test(f"Incorrect Session Rejection", True, f"✅ Correctly rejected invalid format", "VENDING")
                    print(f"  📝 Error Message: {response.text}")
                else:
                    self.log_test(f"Incorrect Session Rejection", False, f"❌ Should have rejected invalid format but got HTTP {response.status_code}", "VENDING")
                    all_rejected = False
                    
            except Exception as e:
                self.log_test(f"Incorrect Session Rejection", False, f"Error: {str(e)}", "VENDING")
                all_rejected = False
        
        return all_rejected

    def test_payment_status_api(self) -> bool:
        """Test payment status API that Chinese developers need access to"""
        print("\n💳 Testing Payment Status API...")
        
        test_third_ids = ["TEST_THIRD_ID_001", "TEST_THIRD_ID_002", "NONEXISTENT_ID"]
        
        all_accessible = True
        for third_id in test_third_ids:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/chinese/payment/{third_id}/status",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get('success', False)
                    if success:
                        self.log_test(f"Payment Status: {third_id}", True, f"Payment found with status {data.get('status')}", "PAYMENT")
                    else:
                        self.log_test(f"Payment Status: {third_id}", True, f"Payment not found (expected): {data.get('error')}", "PAYMENT")
                elif response.status_code == 403:
                    self.log_test(f"Payment Status: {third_id}", False, "❌ ACCESS DENIED - This is the Chinese developer issue!", "PAYMENT")
                    all_accessible = False
                else:
                    self.log_test(f"Payment Status: {third_id}", False, f"HTTP {response.status_code}: {response.text[:200]}", "PAYMENT")
                    all_accessible = False
                    
            except Exception as e:
                self.log_test(f"Payment Status: {third_id}", False, f"Error: {str(e)}", "PAYMENT")
                all_accessible = False
        
        return all_accessible

    def test_chinese_specific_endpoints(self) -> bool:
        """Test all Chinese-specific API endpoints"""
        print("\n🇨🇳 Testing Chinese-Specific Endpoints...")
        
        endpoints_to_test = [
            ("GET", "/api/chinese/test-connection", "Test Connection"),
            ("GET", "/api/chinese/models/stock-status", "Stock Status"),
            ("GET", "/api/chinese/equipment/VM_TEST_MANUFACTURER/info", "Equipment Info")
        ]
        
        all_working = True
        for method, endpoint, name in endpoints_to_test:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", json={}, timeout=10)
                
                success = response.status_code in [200, 201]
                if success:
                    self.log_test(f"Chinese API: {name}", True, f"HTTP {response.status_code} - Accessible", "CHINESE_API")
                else:
                    self.log_test(f"Chinese API: {name}", False, f"HTTP {response.status_code}: {response.text[:200]}", "CHINESE_API")
                    all_working = False
                    
            except Exception as e:
                self.log_test(f"Chinese API: {name}", False, f"Error: {str(e)}", "CHINESE_API")
                all_working = False
        
        return all_working

    def test_payment_status_update(self) -> bool:
        """Test payment status update endpoint"""
        print("\n📤 Testing Payment Status Update...")
        
        test_payload = {
            "third_id": "TEST_CHINESE_PAYMENT_001",
            "status": 3  # Paid status
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chinese/order/payStatus",
                json=test_payload,
                timeout=10
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                self.log_test("Payment Status Update", True, f"Update successful: {data.get('msg', 'No message')}", "PAYMENT")
            else:
                self.log_test("Payment Status Update", False, f"HTTP {response.status_code}: {response.text[:200]}", "PAYMENT")
            
            return success
            
        except Exception as e:
            self.log_test("Payment Status Update", False, f"Error: {str(e)}", "PAYMENT")
            return False

    def run_comprehensive_test(self):
        """Run all tests and generate comprehensive report"""
        print("Starting Comprehensive Chinese API Testing Suite")
        print(f"Target: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_connection():
            print("❌ API connection failed. Cannot continue with other tests.")
            return False
        
        # Run all test suites
        tests = [
            self.test_session_validation_correct,
            self.test_session_validation_incorrect,
            self.test_vending_session_status_correct,
            self.test_vending_session_status_incorrect,
            self.test_payment_status_api,
            self.test_chinese_specific_endpoints,
            self.test_payment_status_update
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
                time.sleep(0.5)  # Brief pause between test suites
            except Exception as e:
                print(f"❌ Test suite failed: {str(e)}")
                results.append(False)
        
        # Generate final report
        self.generate_report(results)
        return all(results)

    def generate_report(self, test_suite_results: List[bool]):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Test suite results
        print(f"\n🔬 Test Suite Results:")
        suite_names = [
            "Session Validation (Correct)",
            "Session Validation (Incorrect)", 
            "Vending Session Status (Correct)",
            "Vending Session Status (Incorrect)",
            "Payment Status API Access",
            "Chinese-Specific Endpoints",
            "Payment Status Update"
        ]
        
        for i, (name, result) in enumerate(zip(suite_names, test_suite_results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {name}")
        
        # Category breakdown
        categories = {}
        for result in self.test_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'passed': 0, 'failed': 0}
            
            if result['success']:
                categories[cat]['passed'] += 1
            else:
                categories[cat]['failed'] += 1
        
        print(f"\n📋 Results by Category:")
        for cat, stats in categories.items():
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total * 100) if total > 0 else 0
            print(f"  {cat}: {stats['passed']}/{total} ({rate:.1f}%)")
        
        # Failed tests details
        failed_tests_list = [r for r in self.test_results if not r['success']]
        if failed_tests_list:
            print(f"\n❌ Failed Tests Details:")
            for test in failed_tests_list:
                print(f"  • {test['test']}: {test['details']}")
        
        print("\n" + "=" * 80)
        print("🎯 CHINESE DEVELOPER MISTAKES IDENTIFIED:")
        print("=" * 80)
        print("1. ❌ Date Format Error: Using '2025729' instead of '20250729'")
        print("2. ❌ URL Parameters: Including '?qr=true&machine_id=...' in session ID")
        print("3. ❌ Case Sensitivity: Using lowercase instead of uppercase")
        print("4. ❌ Time Format: Using '1430' instead of '143000'")
        print("5. ❌ Separator Usage: Using hyphens '-' instead of underscores '_'")
        print("6. ❌ Missing Components: Incomplete session ID parts")
        
        print("\n✅ SOLUTIONS PROVIDED:")
        print("1. ✅ Flexible session validation for Chinese partners")
        print("2. ✅ Debug endpoint: /api/chinese/debug/session-validation/{session_id}")
        print("3. ✅ Machine IDs: 10HKNTDOH2BA, CN_DEBUG_01, VM_TEST_MANUFACTURER")
        print("4. ✅ Detailed error messages with format examples")
        print("5. ✅ Enhanced API documentation with debugging guide")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main execution function"""
    print("Chinese API Testing Suite for Render Deployment")
    print("This tool tests all Chinese manufacturer API endpoints")
    print("and demonstrates the mistakes Chinese developers were making.\n")
    
    # Test against render deployment
    tester = ChineseAPITester("https://pimpmycase.onrender.com")
    
    try:
        success = tester.run_comprehensive_test()
        exit_code = 0 if success else 1
        
        print(f"\n{'ALL TESTS PASSED!' if success else 'SOME TESTS FAILED'}")
        print(f"Exit code: {exit_code}")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()