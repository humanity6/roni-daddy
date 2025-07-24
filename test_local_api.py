#!/usr/bin/env python3
"""
Comprehensive Local API Test Suite for PimpMyCase
Enhanced version with local testing capabilities, reset/init functionality,
and extensive edge case testing for Chinese manufacturer integration.
"""

import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import subprocess
import argparse

class LocalAPITester:
    def __init__(self, base_url: str = "http://localhost:8000", verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        self.verbose = verbose
        self.server_process = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", category: str = "TEST"):
        """Log test result with enhanced formatting"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} {test_name}"
        if details:
            result += f" - {details}"
        
        # Color coding for terminal output
        if success:
            print(f"\033[92m{result}\033[0m")  # Green
        else:
            print(f"\033[91m{result}\033[0m")  # Red
            
        if self.verbose and not success:
            print(f"    💡 Debug info: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": timestamp,
            "category": category
        })
        
    def start_local_server(self, timeout: int = 30) -> bool:
        """Start local FastAPI server for testing"""
        try:
            print("🚀 Starting local FastAPI server...")
            
            # Check if server is already running
            try:
                response = self.session.get(f"{self.base_url}/", timeout=5)
                if response.status_code == 200:
                    print("✅ Server already running")
                    return True
            except:
                pass
            
            # Start server process
            self.server_process = subprocess.Popen([
                sys.executable, "api_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            for i in range(timeout):
                try:
                    response = self.session.get(f"{self.base_url}/", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Server started successfully on {self.base_url}")
                        return True
                except:
                    time.sleep(1)
                    print(f"⏳ Waiting for server... ({i+1}/{timeout})")
            
            print("❌ Failed to start server")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def stop_local_server(self):
        """Stop local FastAPI server"""
        if self.server_process:
            print("🛑 Stopping local server...")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ Server stopped")
    
    def reset_database(self) -> bool:
        """Reset database - local version"""
        try:
            print("🔄 Resetting database...")
            response = self.session.get(f"{self.base_url}/reset-database", timeout=30)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.log_test("Database Reset", success, f"Status: {response.status_code}", "SETUP")
                time.sleep(2)  # Wait for reset to complete
            else:
                self.log_test("Database Reset", success, f"Status: {response.status_code}, Error: {response.text}", "SETUP")
            
            return success
        except Exception as e:
            self.log_test("Database Reset", False, f"Error: {str(e)}", "SETUP")
            return False
    
    def init_database(self) -> bool:
        """Initialize database with test data - local version"""
        try:
            print("📊 Initializing database with test data...")
            response = self.session.get(f"{self.base_url}/init-database", timeout=60)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                initialized_items = data.get('initialized', [])
                details = f"Initialized: {', '.join(initialized_items)}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text}"
            
            self.log_test("Database Initialization", success, details, "SETUP")
            if success:
                time.sleep(3)  # Wait for init to complete
            
            return success
        except Exception as e:
            self.log_test("Database Initialization", False, f"Error: {str(e)}", "SETUP")
            return False
    
    def test_api_health(self) -> bool:
        """Test basic API connectivity with detailed health check"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                openai_status = data.get('openai', {}).get('status', 'unknown')
                db_status = data.get('database', {}).get('status', 'unknown')
                details = f"OpenAI: {openai_status}, Database: {db_status}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("API Health Check", success, details, "HEALTH")
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Error: {str(e)}", "HEALTH")
            return False
    
    def test_chinese_api_comprehensive(self) -> Dict[str, bool]:
        """Comprehensive Chinese API testing"""
        results = {}
        
        # Test connection
        results['connection'] = self.test_chinese_api_connection()
        
        # Test order status updates with various scenarios
        results['order_status_valid'] = self.test_chinese_order_status_scenarios()
        
        # Test print command
        results['print_command'] = self.test_chinese_print_command_scenarios()
        
        # Test phone models endpoint
        results['phone_models'] = self.test_chinese_phone_models()
        
        # Test device heartbeat
        results['device_heartbeat'] = self.test_chinese_device_heartbeat()
        
        return results
    
    def test_chinese_api_connection(self) -> bool:
        """Test Chinese API connection endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/chinese/test-connection")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Version: {data.get('api_version')}, Endpoints: {len(data.get('endpoints', {}))}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Chinese API Connection", success, details, "CHINESE")
            return success
        except Exception as e:
            self.log_test("Chinese API Connection", False, f"Error: {str(e)}", "CHINESE")
            return False
    
    def test_chinese_order_status_scenarios(self) -> bool:
        """Test Chinese API order status with multiple scenarios"""
        test_scenarios = [
            {
                "name": "Valid Test Order",
                "data": {
                    "order_id": "TEST_ORDER_001",
                    "status": "printing",
                    "queue_number": "Q123",
                    "estimated_completion": "2024-01-15T14:30:00.000Z",
                    "chinese_order_id": "CN_ORDER_12345",
                    "notes": "Test order status update"
                },
                "expected_codes": [200, 404]  # 404 acceptable for test orders
            },
            {
                "name": "Invalid Order ID",
                "data": {
                    "order_id": "",
                    "status": "printing"
                },
                "expected_codes": [400]
            },
            {
                "name": "Invalid Status",
                "data": {
                    "order_id": "TEST_ORDER_002",
                    "status": "invalid_status"
                },
                "expected_codes": [400, 404]
            }
        ]
        
        all_passed = True
        for scenario in test_scenarios:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/chinese/order-status-update",
                    json=scenario["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                success = response.status_code in scenario["expected_codes"]
                details = f"Status: {response.status_code} (expected: {scenario['expected_codes']})"
                
                self.log_test(f"Order Status - {scenario['name']}", success, details, "CHINESE")
                
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Order Status - {scenario['name']}", False, f"Error: {str(e)}", "CHINESE")
                all_passed = False
        
        return all_passed
    
    def test_chinese_print_command_scenarios(self) -> bool:
        """Test Chinese print command with multiple scenarios"""
        test_scenarios = [
            {
                "name": "Valid Test Print Command",
                "data": {
                    "order_id": "TEST_ORDER_PRINT_001",
                    "image_urls": ["https://example.com/test1.jpg", "https://example.com/test2.jpg"],
                    "phone_model": "iPhone 15 Pro",
                    "customer_info": {
                        "session_id": "TEST_SESSION",
                        "machine_id": "VM_TEST_MANUFACTURER"
                    },
                    "priority": 1
                },
                "expected_codes": [200]
            },
            {
                "name": "Missing Required Fields",
                "data": {
                    "order_id": "TEST_ORDER_PRINT_002"
                },
                "expected_codes": [400, 422]  # Validation error
            },
            {
                "name": "Large Image URLs Array",
                "data": {
                    "order_id": "TEST_ORDER_PRINT_003",
                    "image_urls": [f"https://example.com/test{i}.jpg" for i in range(20)],
                    "phone_model": "Samsung Galaxy S24",
                    "customer_info": {"test": True},
                    "priority": 5
                },
                "expected_codes": [200, 400]
            }
        ]
        
        all_passed = True
        for scenario in test_scenarios:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/chinese/send-print-command",
                    json=scenario["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                success = response.status_code in scenario["expected_codes"]
                details = f"Status: {response.status_code}"
                if success and response.status_code == 200:
                    data = response.json()
                    details += f", Command ID: {data.get('command_id', 'N/A')}"
                
                self.log_test(f"Print Command - {scenario['name']}", success, details, "CHINESE")
                
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Print Command - {scenario['name']}", False, f"Error: {str(e)}", "CHINESE")
                all_passed = False
        
        return all_passed
    
    def test_chinese_phone_models(self) -> bool:
        """Test Chinese phone models endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/chinese/phone-models")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                total_models = data.get('total_models', 0)
                device_count = len(data.get('device_mappings', {}))
                details += f", Models: {total_models}, Device Mappings: {device_count}"
            
            self.log_test("Chinese Phone Models", success, details, "CHINESE")
            return success
        except Exception as e:
            self.log_test("Chinese Phone Models", False, f"Error: {str(e)}", "CHINESE")
            return False
    
    def test_chinese_device_heartbeat(self) -> bool:
        """Test Chinese device heartbeat endpoint"""
        try:
            test_data = {
                "device_id": "TEST_DEVICE_LOCAL_001",
                "status": "online",
                "timestamp": datetime.now().isoformat(),
                "system_info": {
                    "version": "1.0.0",
                    "free_space_mb": 2048,
                    "temperature_c": 32,
                    "print_queue_size": 3
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chinese/device-heartbeat",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                machine_status = data.get('machine_status', 'unknown')
                active_sessions = data.get('active_sessions', 0)
                details += f", Machine Status: {machine_status}, Active Sessions: {active_sessions}"
            
            self.log_test("Chinese Device Heartbeat", success, details, "CHINESE")
            return success
        except Exception as e:
            self.log_test("Chinese Device Heartbeat", False, f"Error: {str(e)}", "CHINESE")
            return False
    
    def test_complete_qr_flow(self) -> bool:
        """Test complete QR flow with enhanced scenarios"""
        print("\n🔄 Starting Complete QR Flow Test...")
        
        # Step 1: Create session
        session_id = self.test_vending_session_creation()
        if not session_id:
            return False
        
        # Step 2: Check session status
        if not self.test_session_status(session_id):
            return False
        
        # Step 3: Register user (this was previously failing)
        if not self.test_user_registration(session_id):
            return False
        
        # Step 4: Test session validation
        if not self.test_session_validation(session_id):
            return False
        
        # Step 5: Submit order summary
        if not self.test_order_summary(session_id):
            return False
        
        # Step 6: Confirm payment
        if not self.test_payment_confirmation(session_id):
            return False
        
        print("✅ Complete QR flow test successful!")
        return True
    
    def test_vending_session_creation(self) -> Optional[str]:
        """Test vending machine session creation"""
        try:
            test_data = {
                "machine_id": "VM_TEST_MANUFACTURER",
                "location": "Local Testing Environment",
                "session_timeout_minutes": 30,
                "metadata": {
                    "test_type": "local_comprehensive_test",
                    "timestamp": datetime.now().isoformat(),
                    "version": "2.0.0"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/vending/create-session",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            session_id = None
            
            if success:
                data = response.json()
                session_id = data.get("session_id")
                machine_info = data.get("machine_info", {})
                details = f"Session ID: {session_id}, Machine: {machine_info.get('name', 'Unknown')}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text}"
            
            self.log_test("Vending Session Creation", success, details, "QR_FLOW")
            return session_id if success else None
        except Exception as e:
            self.log_test("Vending Session Creation", False, f"Error: {str(e)}", "QR_FLOW")
            return None
    
    def test_session_status(self, session_id: str) -> bool:
        """Test session status retrieval"""
        try:
            response = self.session.get(f"{self.base_url}/api/vending/session/{session_id}/status")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Progress: {data.get('user_progress')}, Security: {data.get('security_validated', False)}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Session Status Check", success, details, "QR_FLOW")
            return success
        except Exception as e:
            self.log_test("Session Status Check", False, f"Error: {str(e)}", "QR_FLOW")
            return False
    
    def test_user_registration(self, session_id: str) -> bool:
        """Test user registration with session (previously failing)"""
        try:
            test_data = {
                "machine_id": "VM_TEST_MANUFACTURER",
                "session_id": session_id,
                "location": "Local Testing Environment",
                "user_agent": "Mozilla/5.0 (compatible; LocalAPITest/2.0)",
                "ip_address": "127.0.0.1"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/vending/session/{session_id}/register-user",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Progress: {data.get('user_progress')}, Security: {data.get('security_validated', False)}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
            
            self.log_test("User Registration", success, details, "QR_FLOW")
            return success
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}", "QR_FLOW")
            return False
    
    def test_session_validation(self, session_id: str) -> bool:
        """Test session security validation"""
        try:
            response = self.session.post(f"{self.base_url}/api/vending/session/{session_id}/validate")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                is_valid = data.get('valid', False)
                security_validated = data.get('security_validated', False)
                details = f"Valid: {is_valid}, Security Validated: {security_validated}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Session Validation", success, details, "QR_FLOW")
            return success
        except Exception as e:
            self.log_test("Session Validation", False, f"Error: {str(e)}", "QR_FLOW")
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
                    "text": "Local API Test Case",
                    "font": "Arial",
                    "color": "#000000",
                    "user_selections": {
                        "brand": "iPhone",
                        "model": "iPhone 15 Pro",
                        "template_category": "ai"
                    }
                },
                "payment_amount": 21.99,
                "currency": "GBP"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/vending/session/{session_id}/order-summary",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Amount: £{data.get('payment_amount')}, Currency: {data.get('currency')}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Order Summary", success, details, "QR_FLOW")
            return success
        except Exception as e:
            self.log_test("Order Summary", False, f"Error: {str(e)}", "QR_FLOW")
            return False
    
    def test_payment_confirmation(self, session_id: str) -> bool:
        """Test payment confirmation"""
        try:
            test_data = {
                "session_id": session_id,
                "payment_method": "card",
                "payment_amount": 21.99,
                "transaction_id": f"LOCAL_TXN_{int(time.time())}",
                "payment_data": {
                    "card_type": "visa",
                    "last_four": "4242",
                    "approval_code": "TEST123",
                    "merchant_ref": "LOCAL_TEST"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/vending/session/{session_id}/confirm-payment",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Transaction: {data.get('transaction_id')}, Status: {data.get('status')}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Payment Confirmation", success, details, "QR_FLOW")
            return success
        except Exception as e:
            self.log_test("Payment Confirmation", False, f"Error: {str(e)}", "QR_FLOW")
            return False
    
    def test_security_scenarios(self) -> Dict[str, bool]:
        """Test various security scenarios"""
        results = {}
        
        # Test rate limiting
        results['rate_limiting'] = self.test_rate_limiting()
        
        # Test invalid session IDs
        results['invalid_session_ids'] = self.test_invalid_session_ids()
        
        # Test session timeout scenarios
        results['session_timeouts'] = self.test_session_timeout_scenarios()
        
        return results
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        try:
            print("🔒 Testing rate limiting (making 35 rapid requests)...")
            rate_limited = False
            
            for i in range(35):
                response = self.session.get(f"{self.base_url}/api/chinese/test-connection")
                if response.status_code == 429:
                    rate_limited = True
                    break
                time.sleep(0.05)  # Small delay between requests
            
            details = "Rate limit triggered as expected" if rate_limited else "Rate limit not triggered - check configuration"
            self.log_test("Rate Limiting", rate_limited, details, "SECURITY")
            return rate_limited
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Error: {str(e)}", "SECURITY")
            return False
    
    def test_invalid_session_ids(self) -> bool:
        """Test various invalid session ID scenarios"""
        invalid_session_ids = [
            ("empty", ""),
            ("too_short", "ABC"),
            ("wrong_format", "invalid-session-id"),
            ("sql_injection", "'; DROP TABLE sessions; --"),
            ("too_long", "A" * 300)
        ]
        
        all_passed = True
        for test_name, session_id in invalid_session_ids:
            try:
                response = self.session.get(f"{self.base_url}/api/vending/session/{session_id}/status")
                success = response.status_code in [400, 404]  # Should reject invalid IDs
                details = f"Status: {response.status_code}"
                
                self.log_test(f"Invalid Session ID - {test_name}", success, details, "SECURITY")
                
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Invalid Session ID - {test_name}", False, f"Error: {str(e)}", "SECURITY")
                all_passed = False
        
        return all_passed
    
    def test_session_timeout_scenarios(self) -> bool:
        """Test session timeout handling"""
        # This is a placeholder for timeout testing - would need special setup
        # For now, just test that expired session detection works
        try:
            # Create a session
            session_id = self.test_vending_session_creation()
            if not session_id:
                return False
            
            # Test immediate access (should work)
            response = self.session.get(f"{self.base_url}/api/vending/session/{session_id}/status")
            immediate_success = response.status_code == 200
            
            self.log_test("Session Timeout - Immediate Access", immediate_success, 
                         f"Status: {response.status_code}", "SECURITY")
            
            return immediate_success
        except Exception as e:
            self.log_test("Session Timeout Test", False, f"Error: {str(e)}", "SECURITY")
            return False
    
    def test_api_endpoints_comprehensive(self) -> Dict[str, bool]:
        """Test all API endpoints comprehensively"""
        results = {}
        
        # Test brand endpoints
        results['brands'] = self.test_brands_endpoint()
        results['phone_models'] = self.test_phone_models_endpoint()
        results['templates'] = self.test_templates_endpoint()
        
        return results
    
    def test_brands_endpoint(self) -> bool:
        """Test brands API endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/brands")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                brands = data.get('brands', [])
                details = f"Found {len(brands)} brands"
                if brands:
                    available_count = sum(1 for b in brands if b.get('is_available'))
                    details += f", {available_count} available"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Brands Endpoint", success, details, "API")
            return success
        except Exception as e:
            self.log_test("Brands Endpoint", False, f"Error: {str(e)}", "API")
            return False
    
    def test_phone_models_endpoint(self) -> bool:
        """Test phone models API endpoint"""
        try:
            # Test iPhone models
            response = self.session.get(f"{self.base_url}/api/brands/iphone/models")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                models = data.get('models', [])
                brand_info = data.get('brand', {})
                details = f"iPhone models: {len(models)}, Brand: {brand_info.get('name', 'Unknown')}"
                
                # Check for chinese_model_id
                if models and 'chinese_model_id' in models[0]:
                    details += ", Chinese IDs present"
                else:
                    details += ", ⚠️  Chinese IDs missing"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Phone Models Endpoint", success, details, "API")
            return success
        except Exception as e:
            self.log_test("Phone Models Endpoint", False, f"Error: {str(e)}", "API")
            return False
    
    def test_templates_endpoint(self) -> bool:
        """Test templates API endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/templates")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                templates = data.get('templates', [])
                ai_templates = [t for t in templates if t.get('category') == 'ai']
                basic_templates = [t for t in templates if t.get('category') == 'basic']
                details = f"Total: {len(templates)}, AI: {len(ai_templates)}, Basic: {len(basic_templates)}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Templates Endpoint", success, details, "API")
            return success
        except Exception as e:
            self.log_test("Templates Endpoint", False, f"Error: {str(e)}", "API")
            return False
    
    def run_comprehensive_test_suite(self, include_server_management: bool = False):
        """Run comprehensive test suite with all categories"""
        print("🧪 Starting Comprehensive Local API Test Suite")
        print(f"🎯 Testing API at: {self.base_url}")
        print("=" * 80)
        
        # Start server if requested
        if include_server_management:
            if not self.start_local_server():
                print("❌ Failed to start server, aborting tests")
                return
        
        try:
            # Health checks
            print("\n🏥 HEALTH CHECKS")
            self.test_api_health()
            
            # Database setup
            print("\n🗄️  DATABASE SETUP")
            if not self.reset_database():
                print("⚠️  Database reset failed, continuing anyway...")
            if not self.init_database():
                print("⚠️  Database init failed, some tests may fail...")
            
            # API endpoint tests
            print("\n🔌 API ENDPOINTS")
            self.test_api_endpoints_comprehensive()
            
            # Chinese manufacturer tests
            print("\n🇨🇳 CHINESE MANUFACTURER API")
            self.test_chinese_api_comprehensive()
            
            # Complete QR flow
            print("\n📱 QR VENDING MACHINE FLOW")
            self.test_complete_qr_flow()
            
            # Security tests
            print("\n🔒 SECURITY TESTS")
            self.test_security_scenarios()
            
            # Print comprehensive summary
            self.print_comprehensive_summary()
            
        finally:
            # Stop server if we started it
            if include_server_management:
                self.stop_local_server()
    
    def print_comprehensive_summary(self):
        """Print comprehensive test results summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            cat = result.get("category", "OTHER")
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
            categories[cat]["tests"].append(result)
        
        # Print category summaries
        total_passed = sum(cat["passed"] for cat in categories.values())
        total_failed = sum(cat["failed"] for cat in categories.values())
        total_tests = total_passed + total_failed
        
        print(f"🎯 OVERALL: {total_passed}/{total_tests} tests passed ({(total_passed/total_tests)*100:.1f}%)")
        print()
        
        for category, stats in categories.items():
            total_cat = stats["passed"] + stats["failed"]
            success_rate = (stats["passed"]/total_cat)*100 if total_cat > 0 else 0
            
            status_icon = "✅" if stats["failed"] == 0 else "⚠️" if success_rate >= 50 else "❌"
            print(f"{status_icon} {category}: {stats['passed']}/{total_cat} passed ({success_rate:.1f}%)")
        
        # List failed tests
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # API readiness assessment
        critical_categories = ["HEALTH", "SETUP", "CHINESE", "QR_FLOW"]
        critical_failed = sum(categories.get(cat, {"failed": 0})["failed"] for cat in critical_categories)
        
        print(f"\n🚦 API STATUS: ", end="")
        if critical_failed == 0:
            print("🟢 READY FOR CHINESE MANUFACTURERS")
        elif critical_failed <= 2:
            print("🟡 MOSTLY READY - Minor issues to address")
        else:
            print("🔴 NEEDS ATTENTION - Critical issues found")
        
        print(f"\n⏰ Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main test runner with command line arguments"""
    parser = argparse.ArgumentParser(description="Comprehensive Local API Test Suite for PimpMyCase")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--start-server", "-s", action="store_true", help="Start local server before testing")
    parser.add_argument("--quick", "-q", action="store_true", help="Run quick test suite only")
    
    args = parser.parse_args()
    
    tester = LocalAPITester(base_url=args.url, verbose=args.verbose)
    
    if args.quick:
        print("⚡ Running Quick Test Suite")
        tester.test_api_health()
        tester.test_chinese_api_connection()
        session_id = tester.test_vending_session_creation()
        if session_id:
            tester.test_user_registration(session_id)
        tester.print_comprehensive_summary()
    else:
        tester.run_comprehensive_test_suite(include_server_management=args.start_server)

if __name__ == "__main__":
    main()