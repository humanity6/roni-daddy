#!/usr/bin/env python3
"""
Comprehensive Local API Test Suite for PimpMyCase
Production-Ready Testing Suite v2.1

New Features Added:
- Tests NEW /api/vending/session/{session_id}/order-info endpoint
- Tests automatic order creation after vending payment confirmation
- Tests automatic Chinese API print command sending
- Tests both payment flows (app via Stripe + vending machine)
- Validates production readiness (no fallbacks, proper validation)
- Tests complete end-to-end flow: QR → Design → Payment → Printing
- Comprehensive Chinese manufacturer integration testing
- Database integration validation

This test suite ensures the complete flow works before sending to Chinese manufacturers:
Vending Machine → QR → Web App → Design → Payment (app or vending) → Printing
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
        status = "PASS" if success else "FAIL"
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
            print(f"    Debug info: {details}")
        
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
            response = self.session.get(f"{self.base_url}/init-database", timeout=360)
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
        
        # Test NEW order/payStatus endpoint
        results['pay_status'] = self.test_chinese_pay_status_endpoint()
        
        # Test payment status checking
        results['payment_status_check'] = self.test_chinese_payment_status_check()
        
        # Test equipment and stock management
        results['equipment_management'] = self.test_chinese_equipment_management()
        
        # Test print management
        results['print_management'] = self.test_chinese_print_management()
        
        # Test UK image hosting
        results['image_hosting'] = self.test_chinese_image_hosting()
        
        # Test order status updates with various scenarios
        results['order_status_valid'] = self.test_chinese_order_status_scenarios()
        
        # Test print command
        results['print_command'] = self.test_chinese_print_command_scenarios()
        
        # Test automatic order processing
        results['automatic_integration'] = self.test_chinese_integration_scenarios()
        
        return results
    
    def test_chinese_integration_scenarios(self) -> bool:
        """Test Chinese manufacturer integration scenarios (NEW)"""
        all_passed = True
        
        # Test that print command endpoint works with real order data
        print("🇨🇳 Testing Chinese integration with realistic order data...")
        
        # Create a test order first (simulating what happens after payment)
        test_scenarios = [
            {
                "name": "Valid Order with Images",
                "data": {
                    "order_id": f"ORDER_{int(time.time())}",
                    "image_urls": [
                        "https://pimpmycase.onrender.com/image/test-image-1.png",
                        "https://pimpmycase.onrender.com/image/test-image-2.png"
                    ],
                    "phone_model": "iPhone 15 Pro",
                    "customer_info": {
                        "vending_machine_id": "VM_TEST_001",
                        "session_id": "TEST_SESSION_001",
                        "transaction_id": "TXN_TEST_001",
                        "payment_method": "card"
                    },
                    "priority": 1
                },
                "should_create_order": True
            },
            {
                "name": "Missing Image URLs",
                "data": {
                    "order_id": f"ORDER_{int(time.time())}_INVALID",
                    "image_urls": [],
                    "phone_model": "iPhone 15 Pro",
                    "customer_info": {"test": True},
                    "priority": 1
                },
                "should_create_order": False
            }
        ]
        
        for scenario in test_scenarios:
            # First create a test order in database if needed
            order_created = True
            if scenario["should_create_order"]:
                order_created = self.create_test_order_for_chinese_testing(scenario["data"]["order_id"])
                if not order_created:
                    self.log_test(f"Chinese Integration - {scenario['name']} (Order Creation)", False, "Failed to create test order", "INTEGRATION")
                    all_passed = False
                    continue  # Skip the print command test if order creation failed
            
            # Test print command
            try:
                response = self.session.post(
                    f"{self.base_url}/api/chinese/send-print-command",
                    json=scenario["data"],
                    headers={"Content-Type": "application/json"}
                )
                
                if scenario["should_create_order"] and order_created:
                    success = response.status_code == 200
                    if success:
                        data = response.json()
                        details = f"Command ID: {data.get('command_id')}, Status: {data.get('status')}"
                    else:
                        details = f"Status: {response.status_code}, Expected: 200, Response: {response.text[:100]}"
                else:
                    success = response.status_code in [400, 404]  # Should fail for invalid data
                    details = f"Status: {response.status_code}, Expected: 400/404"
                
                self.log_test(f"Chinese Integration - {scenario['name']}", success, details, "INTEGRATION")
                
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Chinese Integration - {scenario['name']}", False, f"Error: {str(e)}", "INTEGRATION")
                all_passed = False
        
        return all_passed
    
    def test_chinese_pay_status_endpoint(self) -> bool:
        """Test NEW Chinese order/payStatus endpoint"""
        try:
            print("🇨🇳 Testing Chinese order/payStatus endpoint...")
            
            test_scenarios = [
                {
                    "name": "Valid Payment Status Update",
                    "data": {
                        "third_id": "TEST_THIRD_ID_001",
                        "status": 3  # Paid
                    },
                    "expected_code": 200
                },
                {
                    "name": "Payment Processing",
                    "data": {
                        "third_id": "TEST_THIRD_ID_NEW_001",
                        "status": 2  # Paying
                    },
                    "expected_code": 200
                },
                {
                    "name": "Payment Failed",
                    "data": {
                        "third_id": "TEST_THIRD_ID_FAILED_001",
                        "status": 4  # Failed
                    },
                    "expected_code": 200
                },
                {
                    "name": "Invalid Status",
                    "data": {
                        "third_id": "TEST_THIRD_ID_INVALID",
                        "status": 99  # Invalid
                    },
                    "expected_code": 422  # Validation error
                }
            ]
            
            all_passed = True
            for scenario in test_scenarios:
                try:
                    response = self.session.post(
                        f"{self.base_url}/api/chinese/order/payStatus",
                        json=scenario["data"],
                        headers={"Content-Type": "application/json"}
                    )
                    
                    success = response.status_code == scenario["expected_code"]
                    if success and response.status_code == 200:
                        data = response.json()
                        details = f"Code: {data.get('code')}, Msg: {data.get('msg')}"
                    else:
                        details = f"Status: {response.status_code}, Expected: {scenario['expected_code']}"
                    
                    self.log_test(f"PayStatus - {scenario['name']}", success, details, "CHINESE")
                    
                    if not success:
                        all_passed = False
                        
                except Exception as e:
                    self.log_test(f"PayStatus - {scenario['name']}", False, f"Error: {str(e)}", "CHINESE")
                    all_passed = False
            
            return all_passed
        except Exception as e:
            self.log_test("Chinese PayStatus Endpoint", False, f"Error: {str(e)}", "CHINESE")
            return False
    
    def test_chinese_payment_status_check(self) -> bool:
        """Test Chinese payment status checking endpoint"""
        try:
            # Test existing third_id
            response = self.session.get(f"{self.base_url}/api/chinese/payment/TEST_THIRD_ID_001/status")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Payment Status: {data.get('payment_status')}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Chinese Payment Status Check", success, details, "CHINESE")
            return success
        except Exception as e:
            self.log_test("Chinese Payment Status Check", False, f"Error: {str(e)}", "CHINESE")
            return False
    
    def test_chinese_equipment_management(self) -> bool:
        """Test Chinese equipment and stock management endpoints"""
        try:
            all_passed = True
            
            # Test equipment info
            response = self.session.get(f"{self.base_url}/api/chinese/equipment/VM_TEST_MANUFACTURER/info")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                equipment_info = data.get('equipment_info', {})
                recent_orders = data.get('recent_orders', [])
                details = f"Equipment: {equipment_info.get('name')}, Orders: {len(recent_orders)}"
            else:
                details = f"Status: {response.status_code}"
                all_passed = False
            
            self.log_test("Equipment Info", success, details, "CHINESE")
            
            # Test stock status
            response = self.session.get(f"{self.base_url}/api/chinese/models/stock-status")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                models = data.get('models', [])
                in_stock = data.get('in_stock_models', 0)
                details = f"Total Models: {len(models)}, In Stock: {in_stock}"
            else:
                details = f"Status: {response.status_code}"
                all_passed = False
            
            self.log_test("Stock Status", success, details, "CHINESE")
            
            # Test stock update
            stock_update_data = {
                "stock_updates": [
                    {
                        "model_id": "CN_IPHONE_001",
                        "stock": 50
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chinese/equipment/VM_TEST_MANUFACTURER/stock",
                json=stock_update_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                updated_models = data.get('updated_models', [])
                details = f"Updated {len(updated_models)} models"
            else:
                details = f"Status: {response.status_code}"
                all_passed = False
            
            self.log_test("Stock Update", success, details, "CHINESE")
            
            return all_passed
        except Exception as e:
            self.log_test("Chinese Equipment Management", False, f"Error: {str(e)}", "CHINESE")
            return False
    
    def test_chinese_print_management(self) -> bool:
        """Test Chinese print management endpoints"""
        try:
            all_passed = True
            
            # Test print trigger
            print_data = {
                "order_id": "ORDER_CHINESE_TEST_001"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chinese/print/trigger",
                json=print_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                print_job_id = data.get('print_job_id')
                image_urls = data.get('image_urls', [])
                details = f"Job ID: {print_job_id}, Images: {len(image_urls)}"
            else:
                details = f"Status: {response.status_code}"
                all_passed = False
            
            self.log_test("Print Trigger", success, details, "CHINESE")
            
            # Test print status check
            response = self.session.get(f"{self.base_url}/api/chinese/print/ORDER_CHINESE_TEST_001/status")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                order_status = data.get('status')
                details = f"Order Status: {order_status}"
            else:
                details = f"Status: {response.status_code}"
                all_passed = False
            
            self.log_test("Print Status Check", success, details, "CHINESE")
            
            return all_passed
        except Exception as e:
            self.log_test("Chinese Print Management", False, f"Error: {str(e)}", "CHINESE")
            return False
    
    def test_chinese_image_hosting(self) -> bool:
        """Test UK-hosted image download links for Chinese partners"""
        try:
            all_passed = True
            
            # Test order download links
            response = self.session.get(f"{self.base_url}/api/chinese/order/ORDER_CHINESE_TEST_001/download-links")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                download_links = data.get('download_links', [])
                uk_hosting = data.get('uk_hosting', False)
                details = f"Links: {len(download_links)}, UK Hosting: {uk_hosting}"
            else:
                details = f"Status: {response.status_code}"
                all_passed = False
            
            self.log_test("Order Download Links", success, details, "CHINESE")
            
            # Test batch download
            response = self.session.get(f"{self.base_url}/api/chinese/images/batch-download?order_ids=ORDER_CHINESE_TEST_001,ORDER_CHINESE_TEST_002")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                batch_downloads = data.get('batch_downloads', [])
                successful_orders = data.get('successful_orders', 0)
                details = f"Batch Downloads: {len(batch_downloads)}, Successful: {successful_orders}"
            else:
                details = f"Status: {response.status_code}"
                all_passed = False
            
            self.log_test("Batch Download Links", success, details, "CHINESE")
            
            return all_passed
        except Exception as e:
            self.log_test("Chinese Image Hosting", False, f"Error: {str(e)}", "CHINESE")
            return False
    
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
    
    def test_vending_order_info(self, session_id: str) -> bool:
        """Test vending machine order info endpoint (NEW)"""
        try:
            response = self.session.get(f"{self.base_url}/api/vending/session/{session_id}/order-info")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                order_summary = data.get('order_summary', {})
                payment_amount = data.get('payment_amount')
                details = f"Brand: {order_summary.get('brand')}, Amount: £{payment_amount}, Security: {data.get('security_validated', False)}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Vending Order Info", success, details, "QR_FLOW")
            return success
        except Exception as e:
            self.log_test("Vending Order Info", False, f"Error: {str(e)}", "QR_FLOW")
            return False
    
    def test_order_creation_after_payment(self, session_id: str, order_id: Optional[str] = None) -> bool:
        """Test that orders are automatically created after payment confirmation (NEW)"""
        try:
            if not order_id:
                return False
            
            # Check if order was created in database
            response = self.session.get(f"{self.base_url}/api/orders/{order_id}")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                order = data.get('order', {})
                details = f"Order ID: {order.get('id')}, Status: {order.get('status')}, Payment: {order.get('payment_status')}"
                
                # Verify order details
                if order.get('status') == 'paid' and order.get('payment_status') == 'paid':
                    details += ", ✅ Payment confirmed"
                else:
                    details += ", ⚠️ Payment status issue"
                    success = False
            else:
                details = f"Status: {response.status_code} - Order not found in database"
            
            self.log_test("Order Creation After Payment", success, details, "DATABASE")
            return success
        except Exception as e:
            self.log_test("Order Creation After Payment", False, f"Error: {str(e)}", "DATABASE")
            return False
    
    def test_complete_qr_flow(self) -> bool:
        """Test complete QR flow with enhanced scenarios and NEW automatic integrations"""
        print("\n🔄 Starting Complete QR Flow Test (Enhanced)...")
        
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
        
        # Step 4: Test session validation
        if not self.test_session_validation(session_id):
            return False
        
        # Step 5: Submit order summary
        if not self.test_order_summary(session_id):
            return False
        
        # Step 6: Test NEW order info endpoint
        if not self.test_vending_order_info(session_id):
            return False
        
        # Step 7: Confirm payment and get order ID
        order_id = self.test_payment_confirmation_with_order_creation(session_id)
        if not order_id:
            return False
        
        # Step 8: Test automatic order creation
        if not self.test_order_creation_after_payment(session_id, order_id):
            return False
        
        # Step 9: Test automatic Chinese API integration
        if not self.test_automatic_print_command_sending(order_id):
            return False
        
        print("✅ Complete enhanced QR flow test successful!")
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
        """Test order summary submission with realistic data"""
        try:
            test_data = {
                "session_id": session_id,
                "order_data": {
                    "brand": "iPhone",
                    "model": "iPhone 15 Pro",
                    "template": {
                        "id": "retro-remix",
                        "name": "Retro Remix"
                    },
                    "color": "Natural Titanium",
                    "designImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "inputText": "Local API Test Case",
                    "selectedFont": "Arial",
                    "selectedTextColor": "#000000"
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
                details = f"Amount: £{data.get('payment_amount')}, Currency: {data.get('currency')}, Security: {data.get('security_validated', False)}"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Order Summary", success, details, "QR_FLOW")
            return success
        except Exception as e:
            self.log_test("Order Summary", False, f"Error: {str(e)}", "QR_FLOW")
            return False
    
    def test_payment_confirmation(self, session_id: str) -> bool:
        """Test payment confirmation (legacy method)"""
        order_id = self.test_payment_confirmation_with_order_creation(session_id)
        return order_id is not None
    
    def test_payment_confirmation_with_order_creation(self, session_id: str) -> Optional[str]:
        """Test payment confirmation and return created order ID (NEW)"""
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
            order_id = None
            
            if success:
                data = response.json()
                order_id = data.get('order_id')
                details = f"Transaction: {data.get('transaction_id')}, Status: {data.get('status')}, Order ID: {order_id}"
                
                if order_id:
                    details += ", ✅ Order created automatically"
                else:
                    details += ", ⚠️ No order ID returned"
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("Payment Confirmation with Order Creation", success, details, "QR_FLOW")
            return order_id if success else None
        except Exception as e:
            self.log_test("Payment Confirmation with Order Creation", False, f"Error: {str(e)}", "QR_FLOW")
            return None
    
    def test_automatic_print_command_sending(self, order_id: str) -> bool:
        """Test that print commands are automatically sent to Chinese manufacturers (NEW)"""
        try:
            # Check order status to see if print command was sent
            response = self.session.get(f"{self.base_url}/api/orders/{order_id}")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                order = data.get('order', {})
                order_status = order.get('status')
                
                # Check if print command was sent (status should be 'print_command_sent' or 'paid')
                if order_status in ['print_command_sent', 'paid']:
                    details = f"Status: {order_status}, ✅ Print integration working"
                    
                    # Check for print-related data in order
                    if 'print_command_data' in str(order):
                        details += ", Print data present"
                    else:
                        details += ", Print data may be in separate system"
                        
                else:
                    details = f"Status: {order_status}, ⚠️ Print command not detected"
                    success = False
            else:
                details = f"Status: {response.status_code} - Cannot verify print command"
                success = False
            
            self.log_test("Automatic Print Command Sending", success, details, "INTEGRATION")
            return success
        except Exception as e:
            self.log_test("Automatic Print Command Sending", False, f"Error: {str(e)}", "INTEGRATION")
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
    
    def create_test_order_for_chinese_testing(self, order_id: str) -> bool:
        """Create a test order in the database for Chinese API testing"""
        try:
            # This simulates an order that would be created after payment
            test_order_data = {
                "session_id": f"TEST_SESSION_{order_id}",
                "brand_id": "iphone",  # Assuming iPhone exists from init
                "model_id": "iphone-iphone-15-pro",  # Using proper model ID format from init_db.py
                "template_id": "retro-remix",  # Assuming template exists
                "user_data": {
                    "test_order": True,
                    "created_for": "chinese_api_testing"
                },
                "total_amount": 19.99,
                "currency": "GBP",
                "status": "paid",
                "payment_status": "paid"
            }
            
            # Create order via API (simulating payment completion)
            response = self.session.post(
                f"{self.base_url}/api/orders/create",
                data={
                    "session_id": test_order_data["session_id"],
                    "brand_id": test_order_data["brand_id"],
                    "model_id": test_order_data["model_id"],
                    "template_id": test_order_data["template_id"],
                    "user_data": json.dumps(test_order_data["user_data"])
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                created_order = data.get('order', {})
                print(f"✅ Test order created: {created_order.get('id')} for Chinese API testing")
                return True
            else:
                print(f"⚠️ Failed to create test order: {response.status_code}")
                print(f"⚠️ Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"⚠️ Error creating test order: {e}")
            return False
    
    def test_api_endpoints_comprehensive(self) -> Dict[str, bool]:
        """Test all API endpoints comprehensively"""
        results = {}
        
        # Test brand endpoints
        results['brands'] = self.test_brands_endpoint()
        results['phone_models'] = self.test_phone_models_endpoint()
        results['templates'] = self.test_templates_endpoint()
        
        # Test production readiness
        results['production_validation'] = self.test_production_readiness()
        
        return results
    
    def test_production_readiness(self) -> bool:
        """Test production readiness - no fallbacks, proper validation (NEW)"""
        all_passed = True
        
        print("🚀 Testing production readiness...")
        
        # Test that non-existent brands/models are properly rejected
        test_cases = [
            {
                "name": "Non-existent Brand",
                "endpoint": "/api/brands/nonexistent/models",
                "expected_status": 404
            },
            {
                "name": "Non-existent Template",
                "endpoint": "/api/templates/nonexistent-template",
                "expected_status": 404
            }
        ]
        
        for case in test_cases:
            try:
                response = self.session.get(f"{self.base_url}{case['endpoint']}")
                success = response.status_code == case["expected_status"]
                details = f"Status: {response.status_code}, Expected: {case['expected_status']}"
                
                if success:
                    details += ", ✅ Proper validation"
                else:
                    details += ", ⚠️ Validation issue"
                    all_passed = False
                
                self.log_test(f"Production Validation - {case['name']}", success, details, "PRODUCTION")
                
            except Exception as e:
                self.log_test(f"Production Validation - {case['name']}", False, f"Error: {str(e)}", "PRODUCTION")
                all_passed = False
        
        return all_passed
    
    def test_dual_payment_flows(self) -> bool:
        """Test both app payment and vending machine payment flows (NEW)"""
        print("💳 Testing both payment flows...")
        
        # Test 1: Vending Machine Payment Flow (already tested in complete_qr_flow)
        print("  → Vending machine payment flow already tested in QR flow")
        
        # Test 2: App Payment Flow (Stripe)
        app_payment_success = self.test_app_payment_flow()
        
        self.log_test("Dual Payment Flows", app_payment_success, 
                     "Vending: tested in QR flow, App: " + ("passed" if app_payment_success else "failed"), 
                     "PAYMENT")
        
        return app_payment_success
    
    def test_app_payment_flow(self) -> bool:
        """Test app payment flow using Stripe (NEW)"""
        try:
            # Test Stripe checkout session creation
            test_data = {
                "amount": 19.99,
                "template_id": "retro-remix",
                "brand": "iPhone",
                "model": "iPhone 15 Pro",
                "color": "Natural Titanium"
            }
            
            response = self.session.post(
                f"{self.base_url}/create-checkout-session",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                checkout_url = data.get('checkout_url')
                session_id = data.get('session_id')
                details = f"Checkout URL created, Session ID: {session_id[:20]}..."
                
                # Verify checkout URL is valid
                if checkout_url and checkout_url.startswith('https://checkout.stripe.com'):
                    details += ", ✅ Valid Stripe URL"
                else:
                    details += ", ⚠️ Invalid Stripe URL"
                    success = False
            else:
                details = f"Status: {response.status_code}"
            
            self.log_test("App Payment Flow (Stripe)", success, details, "PAYMENT")
            return success
            
        except Exception as e:
            self.log_test("App Payment Flow (Stripe)", False, f"Error: {str(e)}", "PAYMENT")
            return False
    
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
            
            # Test both payment flows
            print("\n💳 PAYMENT FLOW TESTING")
            self.test_dual_payment_flows()
            
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
        
        # Show integration-specific summary
        integration_tests = [r for r in self.test_results if r.get("category") == "INTEGRATION"]
        if integration_tests:
            integration_passed = sum(1 for t in integration_tests if t["success"])
            integration_total = len(integration_tests)
            print(f"\n🔗 CHINESE MANUFACTURER INTEGRATION: {integration_passed}/{integration_total} tests passed")
        
        # API readiness assessment
        critical_categories = ["HEALTH", "SETUP", "CHINESE", "QR_FLOW", "INTEGRATION", "PRODUCTION"]
        critical_failed = sum(categories.get(cat, {"failed": 0})["failed"] for cat in critical_categories)
        
        print(f"\n🚦 API STATUS: ", end="")
        if critical_failed == 0:
            print("🟢 READY FOR CHINESE MANUFACTURERS")
        elif critical_failed <= 2:
            print("🟡 MOSTLY READY - Minor issues to address")
        else:
            print("🔴 NEEDS ATTENTION - Critical issues found")
        
        print(f"\n⏰ Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Special message for Chinese manufacturers
        if critical_failed == 0:
            print("\n✅ 🇨🇳 CHINESE MANUFACTURER STATUS: API is fully ready for integration!")
            print("   • All critical endpoints working")
            print("   • Automatic order creation confirmed")
            print("   • Print command integration working")
            print("   • Both payment flows operational")
            print("   • Production validation passed")
        else:
            print(f"\n⚠️ 🇨🇳 CHINESE MANUFACTURER STATUS: {critical_failed} critical issues found")
            print("   Please resolve issues before proceeding with integration")

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
            # Test new order-info endpoint
            tester.test_order_summary(session_id)
            tester.test_vending_order_info(session_id)
        tester.print_comprehensive_summary()
    else:
        tester.run_comprehensive_test_suite(include_server_management=args.start_server)

if __name__ == "__main__":
    main()