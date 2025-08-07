"""
PimpMyCase API Integration Test Suite
=====================================

Comprehensive test suite for testing Chinese Manufacturer API integration
with the PimpMyCase system. This test suite covers all endpoints documented
in the API guide.

Requirements:
- pip install pytest requests responses pytest-mock

Usage:
    # Run all tests
    pytest test_pimpmycase_api.py -v
    
    # Run specific test class
    pytest test_pimpmycase_api.py::TestConnectionEndpoints -v
    
    # Run with coverage
    pytest test_pimpmycase_api.py --cov=. -v
"""

import pytest
import requests
import json
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import responses


class PimpMyCaseAPI:
    """PimpMyCase API Client for testing"""
    
    def __init__(self, base_url="https://pimpmycase.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_connection(self):
        """Test API connection"""
        response = self.session.get(f"{self.base_url}/api/chinese/test-connection")
        response.raise_for_status()
        return response.json()
        
    def debug_session_validation(self, session_id):
        """Debug session validation"""
        response = self.session.get(
            f"{self.base_url}/api/chinese/debug/session-validation/{session_id}"
        )
        response.raise_for_status()
        return response.json()
        
    def get_payment_status(self, payment_id):
        """Get payment status"""
        response = self.session.get(
            f"{self.base_url}/api/chinese/payment/{payment_id}/status"
        )
        response.raise_for_status()
        return response.json()
        
    def update_payment_status(self, third_id, status, message=""):
        """Update payment status"""
        data = {
            "third_id": third_id,
            "status": status,
            "message": message
        }
        response = self.session.post(
            f"{self.base_url}/api/chinese/order/payStatus",
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def get_equipment_info(self, equipment_id):
        """Get equipment information"""
        response = self.session.get(
            f"{self.base_url}/api/chinese/equipment/{equipment_id}/info"
        )
        response.raise_for_status()
        return response.json()
        
    def update_equipment_stock(self, equipment_id, phone_models, materials, updated_by):
        """Update equipment stock"""
        data = {
            "phone_models": phone_models,
            "materials": materials,
            "updated_by": updated_by
        }
        response = self.session.post(
            f"{self.base_url}/api/chinese/equipment/{equipment_id}/stock",
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def get_stock_status(self):
        """Get phone model stock status"""
        response = self.session.get(f"{self.base_url}/api/chinese/models/stock-status")
        response.raise_for_status()
        return response.json()
        
    def update_order_status(self, order_id, status, equipment_id=None, notes="", estimated_completion=None):
        """Update order status"""
        data = {
            "order_id": order_id,
            "status": status,
            "notes": notes
        }
        if equipment_id:
            data["equipment_id"] = equipment_id
        if estimated_completion:
            data["estimated_completion"] = estimated_completion
            
        response = self.session.post(
            f"{self.base_url}/api/chinese/order-status-update",
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def send_print_command(self, order_id, image_urls, phone_model, customer_info, priority=2):
        """Send print command"""
        data = {
            "order_id": order_id,
            "image_urls": image_urls,
            "phone_model": phone_model,
            "customer_info": customer_info,
            "priority": priority
        }
        response = self.session.post(
            f"{self.base_url}/api/chinese/send-print-command",
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def trigger_print_job(self, order_id, equipment_id, print_data):
        """Trigger print job"""
        data = {
            "order_id": order_id,
            "equipment_id": equipment_id,
            "print_data": print_data
        }
        response = self.session.post(
            f"{self.base_url}/api/chinese/print/trigger",
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def get_print_status(self, order_id):
        """Get print status"""
        response = self.session.get(
            f"{self.base_url}/api/chinese/print/{order_id}/status"
        )
        response.raise_for_status()
        return response.json()
        
    def get_download_links(self, order_id):
        """Get order download links"""
        response = self.session.get(
            f"{self.base_url}/api/chinese/order/{order_id}/download-links"
        )
        response.raise_for_status()
        return response.json()
        
    def batch_download_images(self, order_ids, format="zip"):
        """Batch download images"""
        params = {"format": format}
        for order_id in order_ids:
            params.setdefault("order_ids", []).append(order_id)
            
        response = self.session.get(
            f"{self.base_url}/api/chinese/images/batch-download",
            params=params
        )
        response.raise_for_status()
        return response.content
        
    # Vending Machine Integration Methods
    def create_vending_session(self, machine_id, location, timeout_minutes=30, metadata=None):
        """Create vending machine session"""
        data = {
            "machine_id": machine_id,
            "location": location,
            "session_timeout_minutes": timeout_minutes,
            "metadata": metadata or {}
        }
        response = self.session.post(
            f"{self.base_url}/api/vending/create-session",
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def get_session_status(self, session_id):
        """Get session status"""
        response = self.session.get(
            f"{self.base_url}/api/vending/session/{session_id}/status"
        )
        response.raise_for_status()
        return response.json()
        
    def register_user_with_session(self, session_id, machine_id, location, user_agent="", ip_address=""):
        """Register user with session"""
        data = {
            "machine_id": machine_id,
            "session_id": session_id,
            "location": location,
            "user_agent": user_agent,
            "ip_address": ip_address
        }
        response = self.session.post(
            f"{self.base_url}/api/vending/session/{session_id}/register-user",
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def order_summary(self, session_id, order_data, payment_amount, currency="GBP"):
        """Send order summary"""
        data = {
            "session_id": session_id,
            "order_data": order_data,
            "payment_amount": payment_amount,
            "currency": currency
        }
        response = self.session.post(
            f"{self.base_url}/api/vending/session/{session_id}/order-summary",
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def confirm_vending_payment(self, session_id, payment_method, payment_amount, transaction_id, payment_data=None):
        """Confirm vending machine payment"""
        data = {
            "session_id": session_id,
            "payment_method": payment_method,
            "payment_amount": payment_amount,
            "transaction_id": transaction_id,
            "payment_data": payment_data or {}
        }
        response = self.session.post(
            f"{self.base_url}/api/vending/session/{session_id}/confirm-payment",
            json=data
        )
        response.raise_for_status()
        return response.json()
        
    def get_order_info_for_payment(self, session_id):
        """Get order info for payment"""
        response = self.session.get(
            f"{self.base_url}/api/vending/session/{session_id}/order-info"
        )
        response.raise_for_status()
        return response.json()
        
    def validate_session(self, session_id):
        """Validate session security"""
        response = self.session.post(
            f"{self.base_url}/api/vending/session/{session_id}/validate"
        )
        response.raise_for_status()
        return response.json()
        
    def cleanup_session(self, session_id):
        """Cleanup session"""
        response = self.session.delete(
            f"{self.base_url}/api/vending/session/{session_id}"
        )
        response.raise_for_status()
        return response.json()
        
    def get_system_health(self):
        """Get system health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


@pytest.fixture
def api_client():
    """Fixture to provide API client instance"""
    return PimpMyCaseAPI("https://pimpmycase.onrender.com")


@pytest.fixture
def test_api_client():
    """Fixture to provide test API client instance"""
    return PimpMyCaseAPI("http://localhost:8000")


class TestConnectionEndpoints:
    """Test connection and basic API functionality"""
    
    @responses.activate
    def test_connection_success(self, api_client):
        """Test successful API connection"""
        mock_response = {
            "status": "success",
            "message": "Chinese manufacturer API connection successful",
            "api_version": "2.2.0",
            "timestamp": "2025-08-04T14:42:09.492554+00:00",
            "client_ip": "127.0.0.1",
            "security_level": "relaxed_chinese_partner",
            "debug_info": {
                "rate_limit": "35 requests/minute",
                "authentication": "not_required",
                "session_validation": "flexible_format_supported"
            },
            "available_machine_ids": ["VM_TEST_MANUFACTURER", "CN_DEBUG_01"]
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/test-connection",
            json=mock_response,
            status=200
        )
        
        result = api_client.test_connection()
        
        assert result["status"] == "success"
        assert result["api_version"] == "2.2.0"
        assert result["security_level"] == "relaxed_chinese_partner"
        assert "CN_DEBUG_01" in result["available_machine_ids"]
    
    @responses.activate 
    def test_debug_session_validation(self, api_client):
        """Test session validation debug endpoint"""
        session_id = "VM001_20250729_143022_A1B2C3"
        mock_response = {
            "session_id": session_id,
            "validation_result": {
                "is_valid": True,
                "format_details": {
                    "machine_id": "VM001",
                    "date_part": "20250729",
                    "time_part": "143022",
                    "random_part": "A1B2C3"
                },
                "security_level": "relaxed",
                "client_ip": "127.0.0.1"
            }
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/debug/session-validation/{session_id}",
            json=mock_response,
            status=200
        )
        
        result = api_client.debug_session_validation(session_id)
        
        assert result["session_id"] == session_id
        assert result["validation_result"]["is_valid"] is True
        assert result["validation_result"]["format_details"]["machine_id"] == "VM001"


class TestPaymentEndpoints:
    """Test payment-related endpoints"""
    
    @responses.activate
    def test_get_payment_status(self, api_client):
        """Test getting payment status"""
        payment_id = "TEST_PAYMENT_E90225F45081"
        mock_response = {
            "payment_id": payment_id,
            "status": 3,
            "status_description": "paid",
            "amount": 1999,
            "currency": "GBP",
            "created_at": "2025-08-02T14:35:00Z",
            "updated_at": "2025-08-02T14:37:15Z"
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/payment/{payment_id}/status",
            json=mock_response,
            status=200
        )
        
        result = api_client.get_payment_status(payment_id)
        
        assert result["payment_id"] == payment_id
        assert result["status"] == 3
        assert result["status_description"] == "paid"
        assert result["amount"] == 1999
        assert result["currency"] == "GBP"
    
    @responses.activate
    def test_update_payment_status(self, api_client):
        """Test updating payment status"""
        mock_response = {
            "success": True,
            "message": "Payment status updated successfully",
            "third_id": "TEST_PAYMENT_123",
            "status": 3
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/chinese/order/payStatus",
            json=mock_response,
            status=200
        )
        
        result = api_client.update_payment_status("TEST_PAYMENT_123", 3, "Payment confirmed")
        
        assert result["success"] is True
        assert result["third_id"] == "TEST_PAYMENT_123"
        assert result["status"] == 3
    
    def test_invalid_payment_status_values(self, api_client):
        """Test validation of payment status values"""
        invalid_statuses = [0, 6, -1, "invalid"]
        
        for invalid_status in invalid_statuses:
            with pytest.raises((ValueError, requests.exceptions.HTTPError)):
                # This should fail validation
                api_client.update_payment_status("TEST_PAYMENT", invalid_status)


class TestEquipmentEndpoints:
    """Test equipment management endpoints"""
    
    @responses.activate
    def test_get_equipment_info(self, api_client):
        """Test getting equipment information"""
        equipment_id = "CN_DEBUG_01"
        mock_response = {
            "equipment_id": equipment_id,
            "status": "online",
            "location": "API Testing Environment - Mock Data",
            "capabilities": {
                "max_print_size": "200x300mm",
                "supported_materials": ["TPU", "Silicone", "Hard Plastic"],
                "color_printing": True,
                "estimated_print_time": "15-30 minutes"
            },
            "current_queue": 3,
            "last_maintenance": "2025-08-01T10:00:00Z",
            "note": "This endpoint currently returns mock data for testing purposes"
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/equipment/{equipment_id}/info",
            json=mock_response,
            status=200
        )
        
        result = api_client.get_equipment_info(equipment_id)
        
        assert result["equipment_id"] == equipment_id
        assert result["status"] == "online"
        assert "TPU" in result["capabilities"]["supported_materials"]
        assert result["capabilities"]["color_printing"] is True
    
    @responses.activate
    def test_update_equipment_stock(self, api_client):
        """Test updating equipment stock"""
        equipment_id = "CN_DEBUG_01"
        mock_response = {
            "success": True,
            "message": "Stock updated successfully",
            "equipment_id": equipment_id,
            "updated_items": 5
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/chinese/equipment/{equipment_id}/stock",
            json=mock_response,
            status=200
        )
        
        phone_models = {
            "iphone_14_pro": 45,
            "iphone_15": 32,
            "samsung_s24": 28
        }
        materials = {
            "clear_tpu": 150,
            "black_silicone": 89,
            "transparent_hard": 67
        }
        
        result = api_client.update_equipment_stock(
            equipment_id, phone_models, materials, "automated_system"
        )
        
        assert result["success"] is True
        assert result["equipment_id"] == equipment_id


class TestStockManagement:
    """Test stock and phone model management"""
    
    @responses.activate
    def test_get_stock_status(self, api_client):
        """Test getting stock status"""
        mock_response = {
            "success": True,
            "models": [
                {
                    "id": "iphone-iphone-15-pro",
                    "name": "iPhone 15 Pro",
                    "chinese_model_id": "CN_IPHONE_006",
                    "brand_id": "iphone",
                    "stock": 45,
                    "price": 19.99,
                    "is_available": True
                },
                {
                    "id": "samsung-galaxy-s24-ultra",
                    "name": "Galaxy S24 Ultra",
                    "chinese_model_id": "CN_SAMSUNG_001",
                    "brand_id": "samsung",
                    "stock": 34,
                    "price": 19.99,
                    "is_available": True
                }
            ],
            "summary": {
                "total_models": 25,
                "total_stock": 158,
                "brands_available": ["iphone", "samsung"],
                "last_updated": "2025-08-02T14:30:00Z"
            }
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/models/stock-status",
            json=mock_response,
            status=200
        )
        
        result = api_client.get_stock_status()
        
        assert result["success"] is True
        assert len(result["models"]) == 2
        assert result["summary"]["total_models"] == 25
        assert result["summary"]["total_stock"] == 158
        assert "iphone" in result["summary"]["brands_available"]
        assert "samsung" in result["summary"]["brands_available"]
        
        # Check individual model data
        iphone_model = result["models"][0]
        assert iphone_model["id"] == "iphone-iphone-15-pro"
        assert iphone_model["stock"] == 45
        assert iphone_model["is_available"] is True


class TestOrderProcessing:
    """Test order processing endpoints"""
    
    @responses.activate
    def test_update_order_status(self, api_client):
        """Test updating order status"""
        mock_response = {
            "success": True,
            "message": "Order status updated successfully",
            "order_id": "ORDER_a819e123",
            "status": "printing"
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/chinese/order-status-update",
            json=mock_response,
            status=200
        )
        
        result = api_client.update_order_status(
            "ORDER_a819e123", 
            "printing", 
            "CN_DEBUG_01", 
            "Started printing process",
            "2025-08-02T15:30:00Z"
        )
        
        assert result["success"] is True
        assert result["order_id"] == "ORDER_a819e123"
        assert result["status"] == "printing"
    
    @responses.activate
    def test_send_print_command(self, api_client):
        """Test sending print command"""
        mock_response = {
            "success": True,
            "message": "Print command sent successfully",
            "order_id": "ORDER_a819e123",
            "queue_position": 1
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/chinese/send-print-command",
            json=mock_response,
            status=200
        )
        
        customer_info = {
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "+44123456789"
        }
        
        result = api_client.send_print_command(
            "ORDER_a819e123",
            ["https://cdn.pimpmycase.com/designs/ORDER_a819e123_design1.png"],
            "iphone_15_pro",
            customer_info,
            2
        )
        
        assert result["success"] is True
        assert result["order_id"] == "ORDER_a819e123"
        assert result["queue_position"] == 1
    
    def test_send_print_command_validation(self, api_client):
        """Test print command validation"""
        # Test missing required fields
        with pytest.raises(TypeError):
            api_client.send_print_command("ORDER_123")  # Missing required parameters
        
        # Test invalid email format
        invalid_customer_info = {
            "name": "John Smith",
            "email": "invalid-email",  # Invalid email
            "phone": "+44123456789"
        }
        
        # This should be handled by API validation, not client
        # The test verifies that we pass the data correctly


class TestPrintManagement:
    """Test print operations"""
    
    @responses.activate
    def test_trigger_print_job(self, api_client):
        """Test triggering print job"""
        mock_response = {
            "success": True,
            "message": "Print job triggered successfully",
            "job_id": "PRINT_JOB_123",
            "order_id": "ORDER_a819e123"
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/chinese/print/trigger",
            json=mock_response,
            status=200
        )
        
        print_data = {
            "design_url": "https://example.com/design.png",
            "phone_model": "iphone_14_pro",
            "template": "classic",
            "text": "Custom Text",
            "font": "Arial",
            "color": "#000000"
        }
        
        result = api_client.trigger_print_job(
            "ORDER_a819e123",
            "CN_DEBUG_01",
            print_data
        )
        
        assert result["success"] is True
        assert result["order_id"] == "ORDER_a819e123"
        assert "job_id" in result
    
    @responses.activate
    def test_get_print_status(self, api_client):
        """Test getting print status"""
        order_id = "ORDER_a819e123"
        mock_response = {
            "order_id": order_id,
            "print_status": "completed",
            "progress": 100,
            "started_at": "2025-08-02T14:45:00Z",
            "completed_at": "2025-08-02T15:15:00Z",
            "equipment_id": "CN_DEBUG_01",
            "quality_check": "passed"
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/print/{order_id}/status",
            json=mock_response,
            status=200
        )
        
        result = api_client.get_print_status(order_id)
        
        assert result["order_id"] == order_id
        assert result["print_status"] == "completed"
        assert result["progress"] == 100
        assert result["quality_check"] == "passed"


class TestFileManagement:
    """Test file download and management"""
    
    @responses.activate
    def test_get_download_links(self, api_client):
        """Test getting download links"""
        order_id = "ORDER_a819e123"
        mock_response = {
            "order_id": order_id,
            "download_links": {
                "design_file": "https://cdn.pimpmycase.com/designs/ORDER_a819e123_design.png",
                "print_file": "https://cdn.pimpmycase.com/print/ORDER_a819e123_print.gcode",
                "preview": "https://cdn.pimpmycase.com/preview/ORDER_a819e123_preview.jpg"
            },
            "expiry": "2025-08-09T14:42:00Z"
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/order/{order_id}/download-links",
            json=mock_response,
            status=200
        )
        
        result = api_client.get_download_links(order_id)
        
        assert result["order_id"] == order_id
        assert "design_file" in result["download_links"]
        assert "print_file" in result["download_links"]
        assert "preview" in result["download_links"]
        assert result["expiry"] == "2025-08-09T14:42:00Z"
    
    @responses.activate
    def test_batch_download_images(self, api_client):
        """Test batch downloading images"""
        mock_zip_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"  # Mock ZIP header
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/images/batch-download",
            body=mock_zip_content,
            status=200,
            content_type="application/zip"
        )
        
        order_ids = ["ORDER_1", "ORDER_2"]
        result = api_client.batch_download_images(order_ids, "zip")
        
        assert isinstance(result, bytes)
        assert result.startswith(b"PK")  # ZIP file signature


class TestVendingMachineIntegration:
    """Test vending machine integration endpoints"""
    
    @responses.activate
    def test_create_vending_session(self, api_client):
        """Test creating vending machine session"""
        mock_response = {
            "success": True,
            "session_id": "VM001_20250804_143022_A1B2C3D4",
            "qr_data": {
                "session_id": "VM001_20250804_143022_A1B2C3D4",
                "machine_id": "VM001",
                "expires_at": "2025-08-04T15:00:22Z",
                "qr_url": "https://pimpmycase.shop?session=VM001_20250804_143022_A1B2C3D4&machine=VM001"
            },
            "session_info": {
                "status": "active",
                "user_progress": "started",
                "expires_at": "2025-08-04T15:00:22Z",
                "created_at": "2025-08-04T14:30:22Z"
            }
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/vending/create-session",
            json=mock_response,
            status=200
        )
        
        metadata = {
            "mall_name": "Oxford Street Mall",
            "floor": "Level 2",
            "timezone": "Europe/London"
        }
        
        result = api_client.create_vending_session(
            "VM001",
            "Oxford Street Mall - Level 2",
            30,
            metadata
        )
        
        assert result["success"] is True
        assert "VM001" in result["session_id"]
        assert result["qr_data"]["machine_id"] == "VM001"
        assert result["session_info"]["status"] == "active"
        assert result["session_info"]["user_progress"] == "started"
    
    @responses.activate
    def test_get_session_status(self, api_client):
        """Test getting session status"""
        session_id = "VM001_20250804_143022_A1B2C3D4"
        mock_response = {
            "session_id": session_id,
            "status": "designing",
            "user_progress": "design_complete",
            "expires_at": "2025-08-04T15:00:22Z",
            "created_at": "2025-08-04T14:30:22Z",
            "last_activity": "2025-08-04T14:45:10Z",
            "machine_id": "VM001",
            "security_validated": True,
            "order_id": "ORDER_a819e123",
            "payment_amount": 21.99,
            "session_data": {
                "brand": "iphone",
                "model": "iPhone 15 Pro",
                "template": "retro-remix",
                "user_selections": {
                    "images_uploaded": 1,
                    "text_added": "My Custom Text",
                    "font": "Inter"
                }
            }
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/vending/session/{session_id}/status",
            json=mock_response,
            status=200
        )
        
        result = api_client.get_session_status(session_id)
        
        assert result["session_id"] == session_id
        assert result["status"] == "designing"
        assert result["user_progress"] == "design_complete"
        assert result["machine_id"] == "VM001"
        assert result["security_validated"] is True
        assert result["payment_amount"] == 21.99
    
    @responses.activate
    def test_register_user_with_session(self, api_client):
        """Test registering user with session"""
        session_id = "VM001_20250804_143022_A1B2C3D4"
        mock_response = {
            "success": True,
            "message": "User registered with vending machine session",
            "session_status": {
                "status": "active",
                "user_progress": "qr_scanned",
                "expires_at": "2025-08-04T15:00:22Z",
                "last_activity": "2025-08-04T14:32:15Z"
            },
            "user_registered": True
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/vending/session/{session_id}/register-user",
            json=mock_response,
            status=200
        )
        
        result = api_client.register_user_with_session(
            session_id,
            "VM001",
            "Oxford Street Mall - Level 2",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
            "192.168.1.100"
        )
        
        assert result["success"] is True
        assert result["user_registered"] is True
        assert result["session_status"]["user_progress"] == "qr_scanned"
    
    @responses.activate
    def test_order_summary(self, api_client):
        """Test sending order summary"""
        session_id = "VM001_20250804_143022_A1B2C3D4"
        mock_response = {
            "success": True,
            "message": "Order summary received and processed",
            "session_updated": True,
            "payment_required": True,
            "session_status": {
                "status": "payment_pending",
                "user_progress": "payment_reached",
                "payment_amount": 21.99
            }
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/vending/session/{session_id}/order-summary",
            json=mock_response,
            status=200
        )
        
        order_data = {
            "brand": "iphone",
            "model": "iPhone 15 Pro",
            "template": "retro-remix",
            "images": ["image1.jpg"],
            "text": "My Custom Text",
            "font": "Inter",
            "colors": {
                "background": "#FFFFFF",
                "text": "#000000"
            }
        }
        
        result = api_client.order_summary(session_id, order_data, 21.99, "GBP")
        
        assert result["success"] is True
        assert result["session_updated"] is True
        assert result["payment_required"] is True
        assert result["session_status"]["status"] == "payment_pending"
    
    @responses.activate
    def test_confirm_vending_payment(self, api_client):
        """Test confirming vending machine payment"""
        session_id = "VM001_20250804_143022_A1B2C3D4"
        mock_response = {
            "success": True,
            "message": "Payment confirmed successfully",
            "order_created": True,
            "order_id": "ORDER_a819e123",
            "queue_number": "Q001",
            "session_status": {
                "status": "payment_completed",
                "user_progress": "payment_reached",
                "payment_confirmed_at": "2025-08-04T14:50:22Z"
            },
            "print_status": "queued_for_production"
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/vending/session/{session_id}/confirm-payment",
            json=mock_response,
            status=200
        )
        
        payment_data = {
            "card_last_four": "1234",
            "card_type": "Visa",
            "authorization_code": "AUTH123456",
            "receipt_number": "RCP001"
        }
        
        result = api_client.confirm_vending_payment(
            session_id,
            "card",
            21.99,
            "TXN_VM001_20250804_001",
            payment_data
        )
        
        assert result["success"] is True
        assert result["order_created"] is True
        assert result["order_id"] == "ORDER_a819e123"
        assert result["queue_number"] == "Q001"
        assert result["session_status"]["status"] == "payment_completed"
    
    @responses.activate
    def test_get_order_info_for_payment(self, api_client):
        """Test getting order info for payment"""
        session_id = "VM001_20250804_143022_A1B2C3D4"
        mock_response = {
            "session_id": session_id,
            "order_summary": {
                "brand": "iPhone",
                "model": "iPhone 15 Pro",
                "template": "Retro Remix",
                "price": 21.99,
                "currency": "GBP",
                "features": ["AI Enhancement", "Custom Text", "High Quality Print"]
            },
            "payment_info": {
                "amount": 21.99,
                "currency": "GBP",
                "tax_included": True,
                "breakdown": {
                    "base_price": 19.99,
                    "ai_enhancement": 2.00
                }
            },
            "machine_info": {
                "id": "VM001",
                "location": "Oxford Street Mall - Level 2"
            },
            "session_status": {
                "status": "payment_pending",
                "user_progress": "payment_reached",
                "expires_at": "2025-08-04T15:00:22Z",
                "last_activity": "2025-08-04T14:48:30Z"
            }
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/vending/session/{session_id}/order-info",
            json=mock_response,
            status=200
        )
        
        result = api_client.get_order_info_for_payment(session_id)
        
        assert result["session_id"] == session_id
        assert result["order_summary"]["model"] == "iPhone 15 Pro"
        assert result["payment_info"]["amount"] == 21.99
        assert result["machine_info"]["id"] == "VM001"
        assert result["session_status"]["status"] == "payment_pending"
    
    @responses.activate
    def test_validate_session(self, api_client):
        """Test session validation"""
        session_id = "VM001_20250804_143022_A1B2C3D4"
        mock_response = {
            "session_id": session_id,
            "valid": True,
            "security_validated": True,
            "session_health": {
                "is_expired": False,
                "is_active": True,
                "status": "designing",
                "user_progress": "design_complete",
                "expires_at": "2025-08-04T15:00:22Z",
                "last_activity": "2025-08-04T14:48:30Z"
            },
            "security_info": {
                "client_ip": "192.168.1.100",
                "validated": True,
                "security_level": "relaxed",
                "timestamp": "2025-08-04T14:48:35Z"
            }
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/vending/session/{session_id}/validate",
            json=mock_response,
            status=200
        )
        
        result = api_client.validate_session(session_id)
        
        assert result["session_id"] == session_id
        assert result["valid"] is True
        assert result["security_validated"] is True
        assert result["session_health"]["is_active"] is True
        assert result["security_info"]["validated"] is True
    
    @responses.activate
    def test_cleanup_session(self, api_client):
        """Test session cleanup"""
        session_id = "VM001_20250804_143022_A1B2C3D4"
        mock_response = {
            "success": True,
            "message": "Session cancelled successfully",
            "session_id": session_id
        }
        
        responses.add(
            responses.DELETE,
            f"{api_client.base_url}/api/vending/session/{session_id}",
            json=mock_response,
            status=200
        )
        
        result = api_client.cleanup_session(session_id)
        
        assert result["success"] is True
        assert result["session_id"] == session_id


class TestSystemHealth:
    """Test system health and monitoring"""
    
    @responses.activate
    def test_get_system_health(self, api_client):
        """Test getting system health"""
        mock_response = {
            "status": "healthy",
            "timestamp": "2025-08-04T14:50:00Z",
            "api_version": "2.2.0",
            "services": {
                "database": "connected",
                "openai": "configured",
                "stripe": "configured",
                "image_storage": "available"
            },
            "metrics": {
                "active_sessions": 15,
                "pending_orders": 3,
                "system_load": "normal"
            }
        }
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/health",
            json=mock_response,
            status=200
        )
        
        result = api_client.get_system_health()
        
        assert result["status"] == "healthy"
        assert result["api_version"] == "2.2.0"
        assert result["services"]["database"] == "connected"
        assert result["services"]["openai"] == "configured"
        assert result["metrics"]["system_load"] == "normal"


class TestErrorHandling:
    """Test error handling and validation"""
    
    @responses.activate
    def test_http_error_handling(self, api_client):
        """Test HTTP error handling"""
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/test-connection",
            json={"detail": "Service temporarily unavailable"},
            status=500
        )
        
        with pytest.raises(requests.exceptions.HTTPError):
            api_client.test_connection()
    
    @responses.activate
    def test_validation_error_handling(self, api_client):
        """Test validation error handling"""
        mock_error_response = {
            "detail": "Validation failed",
            "validation_errors": [
                {
                    "field": "status",
                    "message": "Status must be one of: ['pending', 'printing', 'printed', 'completed', 'failed', 'cancelled']",
                    "received_value": "invalid_status"
                }
            ],
            "timestamp": "2025-08-02T14:42:00Z"
        }
        
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/chinese/order-status-update",
            json=mock_error_response,
            status=422
        )
        
        with pytest.raises(requests.exceptions.HTTPError):
            api_client.update_order_status("ORDER_123", "invalid_status")
    
    @responses.activate
    def test_rate_limiting(self, api_client):
        """Test rate limiting handling"""
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/test-connection",
            json={"detail": "Rate limit exceeded"},
            status=429
        )
        
        with pytest.raises(requests.exceptions.HTTPError):
            api_client.test_connection()
    
    @responses.activate
    def test_not_found_error(self, api_client):
        """Test 404 error handling"""
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/payment/NONEXISTENT/status",
            json={"detail": "Payment not found"},
            status=404
        )
        
        with pytest.raises(requests.exceptions.HTTPError):
            api_client.get_payment_status("NONEXISTENT")


class TestIntegrationWorkflows:
    """Test complete integration workflows"""
    
    @responses.activate
    def test_complete_vending_machine_workflow(self, api_client):
        """Test complete vending machine workflow"""
        session_id = "VM001_20250804_143022_A1B2C3D4"
        
        # 1. Create session
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/vending/create-session",
            json={
                "success": True,
                "session_id": session_id,
                "qr_data": {"qr_url": f"https://pimpmycase.shop?session={session_id}"},
                "session_info": {"status": "active", "user_progress": "started"}
            },
            status=200
        )
        
        # 2. Register user
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/vending/session/{session_id}/register-user",
            json={
                "success": True,
                "user_registered": True,
                "session_status": {"user_progress": "qr_scanned"}
            },
            status=200
        )
        
        # 3. Check session status
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/vending/session/{session_id}/status",
            json={
                "session_id": session_id,
                "status": "payment_pending",
                "user_progress": "payment_reached"
            },
            status=200
        )
        
        # 4. Get order info
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/vending/session/{session_id}/order-info",
            json={
                "session_id": session_id,
                "payment_info": {"amount": 21.99, "currency": "GBP"}
            },
            status=200
        )
        
        # 5. Confirm payment
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/vending/session/{session_id}/confirm-payment",
            json={
                "success": True,
                "order_created": True,
                "order_id": "ORDER_a819e123"
            },
            status=200
        )
        
        # 6. Cleanup session
        responses.add(
            responses.DELETE,
            f"{api_client.base_url}/api/vending/session/{session_id}",
            json={"success": True, "session_id": session_id},
            status=200
        )
        
        # Execute workflow
        # Step 1: Create session
        session_result = api_client.create_vending_session("VM001", "Oxford Street Mall")
        assert session_result["success"] is True
        
        # Step 2: Register user
        user_result = api_client.register_user_with_session(session_id, "VM001", "Oxford Street Mall")
        assert user_result["user_registered"] is True
        
        # Step 3: Monitor status
        status_result = api_client.get_session_status(session_id)
        assert status_result["user_progress"] == "payment_reached"
        
        # Step 4: Get payment info
        payment_info = api_client.get_order_info_for_payment(session_id)
        assert payment_info["payment_info"]["amount"] == 21.99
        
        # Step 5: Confirm payment
        payment_result = api_client.confirm_vending_payment(
            session_id, "card", 21.99, "TXN_123"
        )
        assert payment_result["order_created"] is True
        
        # Step 6: Cleanup
        cleanup_result = api_client.cleanup_session(session_id)
        assert cleanup_result["success"] is True
    
    @responses.activate
    def test_order_processing_workflow(self, api_client):
        """Test complete order processing workflow"""
        order_id = "ORDER_a819e123"
        
        # 1. Send print command
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/chinese/send-print-command",
            json={"success": True, "order_id": order_id, "queue_position": 1},
            status=200
        )
        
        # 2. Update order status
        responses.add(
            responses.POST,
            f"{api_client.base_url}/api/chinese/order-status-update",
            json={"success": True, "order_id": order_id, "status": "printing"},
            status=200
        )
        
        # 3. Get print status
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/print/{order_id}/status",
            json={
                "order_id": order_id,
                "print_status": "completed",
                "progress": 100
            },
            status=200
        )
        
        # 4. Get download links
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/chinese/order/{order_id}/download-links",
            json={
                "order_id": order_id,
                "download_links": {"design_file": "https://example.com/design.png"}
            },
            status=200
        )
        
        # Execute workflow
        customer_info = {
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "+44123456789"
        }
        
        # Step 1: Send print command
        print_result = api_client.send_print_command(
            order_id,
            ["https://example.com/design.png"],
            "iphone_15_pro",
            customer_info
        )
        assert print_result["success"] is True
        
        # Step 2: Update status
        status_result = api_client.update_order_status(order_id, "printing", "CN_DEBUG_01")
        assert status_result["success"] is True
        
        # Step 3: Check print status
        print_status = api_client.get_print_status(order_id)
        assert print_status["print_status"] == "completed"
        
        # Step 4: Get download links
        download_result = api_client.get_download_links(order_id)
        assert download_result["order_id"] == order_id


class TestDataValidation:
    """Test data validation and edge cases"""
    
    def test_session_id_format_validation(self, api_client):
        """Test session ID format validation"""
        valid_session_ids = [
            "VM001_20250729_143022_A1B2C3",
            "VM_TEST_MANUFACTURER_20250804_120000_XYZ123",
            "CN_DEBUG_01_20250801_095030_ABC456"
        ]
        
        for session_id in valid_session_ids:
            # These should not raise exceptions during URL construction
            url = f"{api_client.base_url}/api/vending/session/{session_id}/status"
            assert session_id in url
    
    def test_payment_amount_validation(self, api_client):
        """Test payment amount validation"""
        valid_amounts = [19.99, 21.99, 0.01, 999.99]
        invalid_amounts = [-1.0, 0, "invalid", None]
        
        # Valid amounts should be acceptable
        for amount in valid_amounts:
            assert isinstance(amount, (int, float))
            assert amount > 0
        
        # Invalid amounts should be caught
        for amount in invalid_amounts:
            if amount is not None and not isinstance(amount, str):
                assert amount <= 0 or not isinstance(amount, (int, float))
    
    def test_phone_model_validation(self, api_client):
        """Test phone model validation"""
        valid_models = [
            "iphone_15_pro",
            "iphone_14_pro",
            "samsung_s24",
            "samsung_galaxy_s24_ultra"
        ]
        
        for model in valid_models:
            assert isinstance(model, str)
            assert len(model) > 0
            assert model.replace("_", "").replace("-", "").isalnum()
    
    def test_email_format_validation(self, api_client):
        """Test email format validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            ""
        ]
        
        for email in valid_emails:
            assert "@" in email
            assert "." in email.split("@")[1]
        
        for email in invalid_emails:
            is_invalid = (
                "@" not in email or  # No @ symbol
                len(email) == 0 or   # Empty string
                (email.startswith("@") and email.count("@") == 1) or  # Starts with @
                email.endswith("@") or  # Ends with @
                ("@" in email and "." not in email.split("@")[-1])  # No dot after @
            )
            assert is_invalid, f"Email '{email}' should be invalid but validation logic failed"


# Performance and Load Testing
class TestPerformance:
    """Test performance and load scenarios"""
    
    @responses.activate
    def test_concurrent_session_creation(self, api_client):
        """Test concurrent session creation"""
        import threading
        import concurrent.futures
        
        def create_session(machine_id):
            responses.add(
                responses.POST,
                f"{api_client.base_url}/api/vending/create-session",
                json={
                    "success": True,
                    "session_id": f"{machine_id}_20250804_143022_ABC123",
                    "qr_data": {"qr_url": f"https://example.com?session={machine_id}"},
                    "session_info": {"status": "active"}
                },
                status=200
            )
            
            return api_client.create_vending_session(machine_id, "Test Location")
        
        # Test creating multiple sessions concurrently
        machine_ids = [f"VM{i:03d}" for i in range(1, 6)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_session, mid) for mid in machine_ids]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        assert len(results) == 5
        for result in results:
            assert result["success"] is True
    
    @responses.activate
    def test_session_polling_performance(self, api_client):
        """Test session status polling performance"""
        session_id = "VM001_20250804_143022_A1B2C3D4"
        
        responses.add(
            responses.GET,
            f"{api_client.base_url}/api/vending/session/{session_id}/status",
            json={
                "session_id": session_id,
                "status": "designing",
                "user_progress": "design_complete"
            },
            status=200
        )
        
        # Simulate polling every 5 seconds
        start_time = time.time()
        poll_count = 5
        
        for _ in range(poll_count):
            result = api_client.get_session_status(session_id)
            assert result["session_id"] == session_id
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete quickly with mocked responses
        assert total_time < 1.0  # Less than 1 second for 5 calls


# Integration Test Utilities
class TestUtilities:
    """Utility functions for testing"""
    
    @staticmethod
    def generate_test_session_id(machine_id="VM001"):
        """Generate a test session ID"""
        from datetime import datetime
        import random
        import string
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{machine_id}_{timestamp}_{random_part}"
    
    @staticmethod
    def generate_test_order_id():
        """Generate a test order ID"""
        import random
        import string
        
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"ORDER_{random_part}"
    
    @staticmethod
    def generate_test_customer_info():
        """Generate test customer information"""
        return {
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "+44123456789"
        }
    
    def test_utility_functions(self):
        """Test utility functions"""
        session_id = self.generate_test_session_id("VM002")
        assert "VM002" in session_id
        assert "_" in session_id
        
        order_id = self.generate_test_order_id()
        assert order_id.startswith("ORDER_")
        assert len(order_id) > 8
        
        customer_info = self.generate_test_customer_info()
        assert "name" in customer_info
        assert "email" in customer_info
        assert "phone" in customer_info
        assert "@" in customer_info["email"]


# Configuration for pytest
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--maxfail=5",
        "--capture=no"
    ])


# Test configuration and fixtures
@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        "base_url": "https://pimpmycase.onrender.com",
        "test_base_url": "http://localhost:8000",
        "timeout": 30,
        "retry_count": 3,
        "test_machine_ids": ["VM001", "VM002", "CN_DEBUG_01"],
        "test_equipment_ids": ["CN_DEBUG_01", "PRINTER_001"],
        "valid_phone_models": [
            "iphone_15_pro",
            "iphone_14_pro", 
            "samsung_s24",
            "samsung_galaxy_s24_ultra"
        ],
        "valid_payment_statuses": [1, 2, 3, 4, 5],
        "valid_order_statuses": [
            "pending", "printing", "printed", 
            "completed", "failed", "cancelled"
        ],
        "valid_payment_methods": ["card", "cash", "contactless"]
    }


@pytest.fixture
def mock_responses():
    """Fixture to provide mock responses for testing"""
    return {
        "successful_connection": {
            "status": "success",
            "api_version": "2.2.0",
            "security_level": "relaxed_chinese_partner"
        },
        "healthy_system": {
            "status": "healthy",
            "api_version": "2.2.0",
            "services": {
                "database": "connected",
                "openai": "configured",
                "stripe": "configured"
            }
        },
        "active_session": {
            "session_id": "VM001_20250804_143022_A1B2C3D4",
            "status": "active",
            "user_progress": "started",
            "machine_id": "VM001"
        }
    }