import requests
import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChineseAPIConfig:
    """Configuration for Chinese API"""
    base_url: str = "http://app-dev.deligp.com:8500/mobileShell/en"
    account: str = "taharizvi.ai@gmail.com"
    password: str = "EN112233"
    system_name: str = "mobileShell"
    fixed_key: str = "shfoa3sfwoehnf3290rqefiz4efd"
    device_id: str = "TEST_DEVICE_001"
    timeout: int = 30

class ChineseAPIClient:
    """Client for Chinese API integration with authentication and signature generation"""
    
    def __init__(self, config: ChineseAPIConfig):
        self.config = config
        self.token = None
        self.token_expires_at = None
        self.session = requests.Session()
        
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
        raw_string = value_string + self.config.system_name + self.config.fixed_key
        
        # Generate MD5 hash
        sign = hashlib.md5(raw_string.encode('utf-8')).hexdigest()
        
        logger.debug(f"Signature generation - Raw string: {raw_string}")
        logger.debug(f"Generated signature: {sign}")
        
        return sign
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any], use_token: bool = False) -> requests.Response:
        """Make API request with proper headers and signature"""
        url = f"{self.config.base_url}/{endpoint}"
        
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
        
        # Log request (mask sensitive information)
        masked_payload = {**payload}
        if "password" in masked_payload:
            masked_payload["password"] = "***"
        
        logger.info(f"Making request to {url}")
        logger.debug(f"Request payload: {masked_payload}")
        
        # Make request
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout)
            
            logger.info(f"Response status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Request failed with status {response.status_code}: {response.text}")
                
            return response
            
        except requests.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise
    
    def _check_response(self, response: requests.Response) -> Dict[str, Any]:
        """Check response and return JSON data"""
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        try:
            res_json = response.json()
        except ValueError:
            raise Exception(f"Invalid JSON response: {response.text}")
        
        if res_json.get("code") != 200:
            raise Exception(f"API Error {res_json.get('code')}: {res_json.get('msg')}")
        
        return res_json
    
    def login(self) -> bool:
        """Login to Chinese API and store token"""
        try:
            payload = {
                "account": self.config.account,
                "password": self.config.password
            }
            
            response = self._make_request("user/login", payload)
            res_json = self._check_response(response)
            
            self.token = res_json["data"]["token"]
            self.token_expires_at = time.time() + (1440 * 60)  # 1440 minutes
            
            logger.info(f"Login successful for account: {self.config.account}")
            logger.debug(f"Token: {self.token[:50]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def ensure_authenticated(self) -> bool:
        """Ensure we have a valid token"""
        if not self.token or (self.token_expires_at and time.time() >= self.token_expires_at):
            return self.login()
        return True
    
    def get_brands(self) -> List[Dict[str, Any]]:
        """Get available phone brands"""
        if not self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        try:
            response = self._make_request("brand/list", {}, use_token=True)
            res_json = self._check_response(response)
            
            brands = res_json.get("data", [])
            logger.info(f"Retrieved {len(brands)} brands")
            
            return brands
            
        except Exception as e:
            logger.error(f"Failed to get brands: {e}")
            raise
    
    def get_stock_list(self, brand_id: str) -> List[Dict[str, Any]]:
        """Get stock list for a specific brand"""
        if not self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        try:
            payload = {
                "device_id": self.config.device_id,
                "brand_id": brand_id
            }
            
            response = self._make_request("stock/list", payload, use_token=True)
            res_json = self._check_response(response)
            
            stocks = res_json.get("data", [])
            logger.info(f"Retrieved {len(stocks)} models for brand {brand_id}")
            
            return stocks
            
        except Exception as e:
            logger.error(f"Failed to get stock list for brand {brand_id}: {e}")
            raise
    
    def upload_file(self, file_path: str, file_content: bytes) -> str:
        """Upload a file and return the URL"""
        if not self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        try:
            url = f"{self.config.base_url}/file/upload"
            
            # For file uploads, we sign the form data parameters
            form_data = {"type": "23"}  # British pictures type
            sign = self.generate_signature(form_data)
            
            headers = {
                "req_source": "en",
                "sign": sign,
                "Authorization": self.token
            }
            
            files = {"file": (file_path, file_content, "image/png")}
            data = {"type": "23"}
            
            response = self.session.post(url, files=files, data=data, headers=headers, timeout=self.config.timeout)
            res_json = self._check_response(response)
            
            file_url = res_json.get("data")
            logger.info(f"File uploaded successfully: {file_url}")
            
            return file_url
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def report_payment(self, mobile_model_id: str, pay_amount: float, pay_type: int = 6) -> Dict[str, Any]:
        """Report payment information"""
        if not self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        try:
            # Generate third-party payment ID
            now = datetime.now()
            third_id = f"PYEN{now.strftime('%y%m%d')}{now.strftime('%H%M%S')}"
            
            payload = {
                "mobile_model_id": mobile_model_id,
                "device_id": self.config.device_id,
                "third_id": third_id,
                "pay_amount": pay_amount,
                "pay_type": pay_type  # 6 = Card
            }
            
            response = self._make_request("order/payData", payload, use_token=True)
            res_json = self._check_response(response)
            
            logger.info(f"Payment reported successfully: {third_id}")
            
            return {
                "third_id": third_id,
                "payment_id": res_json["data"]["id"],
                "amount": pay_amount
            }
            
        except Exception as e:
            logger.error(f"Failed to report payment: {e}")
            raise
    
    def create_order(self, third_pay_id: str, mobile_model_id: str, pic_url: str) -> Dict[str, Any]:
        """Create an order"""
        if not self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        try:
            # Generate third-party order ID
            now = datetime.now()
            third_id = f"OREN{now.strftime('%y%m%d')}{now.strftime('%H%M%S')}"
            
            payload = {
                "third_pay_id": third_pay_id,
                "third_id": third_id,
                "mobile_model_id": mobile_model_id,
                "pic": pic_url,
                "device_id": self.config.device_id
            }
            
            response = self._make_request("order/orderData", payload, use_token=True)
            res_json = self._check_response(response)
            
            logger.info(f"Order created successfully: {third_id}")
            
            return {
                "third_id": third_id,
                "order_id": res_json["data"]["id"],
                "queue_no": res_json["data"]["queue_no"],
                "status": res_json["data"]["status"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            raise
    
    def get_printing_list(self) -> List[Dict[str, Any]]:
        """Get printing list"""
        if not self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        try:
            payload = {
                "device_id": self.config.device_id
            }
            
            response = self._make_request("order/printList", payload, use_token=True)
            res_json = self._check_response(response)
            
            orders = res_json.get("data", [])
            logger.info(f"Retrieved {len(orders)} orders in printing queue")
            
            return orders
            
        except Exception as e:
            logger.error(f"Failed to get printing list: {e}")
            raise
    
    def get_payment_status(self, third_ids: List[str]) -> List[Dict[str, Any]]:
        """Get payment status for given third-party IDs"""
        if not self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        try:
            # Note: The API expects a list as the payload directly
            response = self._make_request("order/getPayStatus", third_ids, use_token=True)
            res_json = self._check_response(response)
            
            statuses = res_json.get("data", [])
            logger.info(f"Retrieved payment status for {len(statuses)} payments")
            
            return statuses
            
        except Exception as e:
            logger.error(f"Failed to get payment status: {e}")
            raise
    
    def get_order_status(self, third_ids: List[str]) -> List[Dict[str, Any]]:
        """Get order status for given third-party IDs"""
        if not self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        try:
            # Note: The API expects a list as the payload directly
            response = self._make_request("order/getOrderStatus", third_ids, use_token=True)
            res_json = self._check_response(response)
            
            statuses = res_json.get("data", [])
            logger.info(f"Retrieved order status for {len(statuses)} orders")
            
            return statuses
            
        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if Chinese API is available"""
        try:
            return self.login()
        except Exception:
            return False 