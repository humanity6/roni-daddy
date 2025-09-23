"""Chinese manufacturer API service"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass
from backend.config.settings import (
    CHINESE_API_BASE_URL, CHINESE_API_ACCOUNT, CHINESE_API_PASSWORD,
    CHINESE_API_SYSTEM_NAME, CHINESE_API_FIXED_KEY, CHINESE_API_TIMEOUT
)

@dataclass
class ChineseAPIConfig:
    """Configuration for Chinese API loaded from environment variables"""
    base_url: str = CHINESE_API_BASE_URL
    account: str = CHINESE_API_ACCOUNT
    password: str = CHINESE_API_PASSWORD
    system_name: str = CHINESE_API_SYSTEM_NAME
    fixed_key: str = CHINESE_API_FIXED_KEY
    req_source: str = "en"
    timeout: int = CHINESE_API_TIMEOUT

class ChineseAPIService:
    """Service for communicating with Chinese manufacturer API"""

    def __init__(self):
        self.config = ChineseAPIConfig()
        self.token = None
        self.session = requests.Session()
        self._is_mock_mode = "localhost" in self.config.base_url.lower()

        # Log which API mode is active
        if self._is_mock_mode:
            print(f"🔧 DEVELOPMENT MODE: Using Chinese API Mock at {self.config.base_url}")
        else:
            print(f"🌐 PRODUCTION MODE: Using real Chinese API at {self.config.base_url}")

    def is_mock_mode(self) -> bool:
        """Check if service is running in mock mode"""
        return self._is_mock_mode

    def _log_payload_keys(self, endpoint: str, payload: Dict[str, Any]) -> None:
        """Log hash of payload keys to detect field drift"""
        import hashlib
        keys = sorted(payload.keys())
        keys_string = ",".join(keys)
        keys_hash = hashlib.md5(keys_string.encode()).hexdigest()[:8]

        print(f"🔑 {endpoint} payload keys hash: {keys_hash} (keys: {keys_string})")

        # Expected hashes for known endpoints (update when API changes intentionally)
        expected_hashes = {
            "orderData": "a1b2c3d4"  # Update this when orderData payload changes
        }

        if endpoint in expected_hashes:
            expected = expected_hashes[endpoint]
            if keys_hash != expected:
                print(f"⚠️  WARNING: {endpoint} payload keys changed!")
                print(f"   Expected hash: {expected}")
                print(f"   Current hash: {keys_hash}")
                print(f"   This may indicate API contract drift")
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate MD5 signature for API request"""
        # Sort parameters by key
        sorted_params = dict(sorted(params.items()))
        
        # Concatenate values
        signature_string = ""
        for key in sorted(sorted_params.keys()):
            value = sorted_params[key]
            if value is not None:
                signature_string += str(value)
        
        # Add system name and fixed key
        signature_string += self.config.system_name
        signature_string += self.config.fixed_key
        
        # Generate MD5 hash
        signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()
        try:
            print(f"Generated signature for params {params}: {signature}")
        except UnicodeEncodeError:
            print(f"Generated signature (params contain non-ASCII): {signature}")
        
        return signature
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any], needs_auth: bool = True) -> Dict[str, Any]:
        """Make authenticated request to Chinese API"""
        if needs_auth and not self.token:
            login_result = self.login()
            if not login_result.get("success"):
                raise Exception(f"Authentication failed: {login_result.get('error')}")
        
        signature = self._generate_signature(payload)
        
        headers = {
            "Content-Type": "application/json",
            "sign": signature,
            "req_source": self.config.req_source
        }
        
        if needs_auth and self.token:
            headers["Authorization"] = self.token
        
        url = f"{self.config.base_url}/{endpoint}"
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout
            )
            response.encoding = 'utf-8'  # Ensure proper encoding
            
            if response.status_code == 200:
                data = response.json()
                try:
                    print(f"Chinese API response for {endpoint}: {data}")
                except UnicodeEncodeError:
                    print(f"Chinese API response for {endpoint}: [response contains non-ASCII characters]")
                return {
                    "success": data.get("code") == 200,
                    "data": data,
                    "message": data.get("msg", "Success")
                }
            else:
                try:
                    error_text = response.text
                except UnicodeDecodeError:
                    error_text = "[response contains non-decodable characters]"
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}",
                    "data": None
                }
        except Exception as e:
            try:
                error_msg = str(e)
            except UnicodeEncodeError:
                error_msg = "Error contains non-ASCII characters - connection or encoding issue"
            return {
                "success": False,
                "error": error_msg,
                "data": None
            }
    
    def login(self) -> Dict[str, Any]:
        """Login and get authentication token"""
        login_data = {
            "account": self.config.account,
            "password": self.config.password
        }
        
        result = self._make_request("user/login", login_data, needs_auth=False)
        
        if result.get("success") and result.get("data", {}).get("data", {}).get("token"):
            self.token = result["data"]["data"]["token"]
            try:
                print(f"Chinese API login successful, token: {self.token[:20]}...")
            except UnicodeEncodeError:
                print("Chinese API login successful, token received")
        
        return result
    
    def get_brands(self) -> Dict[str, Any]:
        """Get available brands from Chinese API"""
        return self._make_request("brand/list", {})
    
    def get_stock_models(self, device_id: str, brand_id: str) -> Dict[str, Any]:
        """Get stock models for a specific device and brand"""
        payload = {
            "device_id": device_id,
            "brand_id": brand_id
        }
        return self._make_request("stock/list", payload)
    
    def send_payment_data(self, mobile_model_id: str, device_id: str, third_id: str, 
                         pay_amount: float, pay_type: int) -> Dict[str, Any]:
        """Send payment data to Chinese API"""
        payload = {
            "mobile_model_id": mobile_model_id,
            "device_id": device_id,
            "third_id": third_id,
            "pay_amount": pay_amount,
            "pay_type": pay_type
        }
        return self._make_request("order/payData", payload)
    
    def get_payment_status(self, third_ids: List[str]) -> Dict[str, Any]:
        """Get payment status for multiple third party IDs"""
        # For payment status, we send a list directly as payload
        try:
            if not self.token:
                login_result = self.login()
                if not login_result.get("success"):
                    raise Exception(f"Authentication failed: {login_result.get('error')}")
            
            # Special handling for payment status - payload is a list
            signature_data = {"third_ids": third_ids}  # Use dict for signature generation
            signature = self._generate_signature(signature_data)
            
            headers = {
                "Content-Type": "application/json",
                "sign": signature,
                "req_source": self.config.req_source,
                "Authorization": self.token
            }
            
            url = f"{self.config.base_url}/order/getPayStatus"
            
            response = self.session.post(
                url,
                json=third_ids,  # Send list directly
                headers=headers,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": data.get("code") == 200,
                    "data": data,
                    "message": data.get("msg", "Success")
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def send_order_data(self, third_pay_id: str, third_id: str, mobile_model_id: str,
                       pic: str, device_id: str, mobile_shell_id: str) -> Dict[str, Any]:
        """Send order data to Chinese API"""
        payload = {
            "third_pay_id": third_pay_id,
            "third_id": third_id,
            "mobile_model_id": mobile_model_id,
            "pic": pic,
            "device_id": device_id,
            "mobile_shell_id": mobile_shell_id
        }

        # Log payload key hash for drift detection
        self._log_payload_keys("orderData", payload)

        return self._make_request("order/orderData", payload)
    
    def get_order_status(self, third_ids: List[str]) -> Dict[str, Any]:
        """Get order status for multiple third party IDs"""
        # Similar to payment status, send list directly
        try:
            if not self.token:
                login_result = self.login()
                if not login_result.get("success"):
                    raise Exception(f"Authentication failed: {login_result.get('error')}")
            
            signature_data = {"third_ids": third_ids}
            signature = self._generate_signature(signature_data)
            
            headers = {
                "Content-Type": "application/json",
                "sign": signature,
                "req_source": self.config.req_source,
                "Authorization": self.token
            }
            
            url = f"{self.config.base_url}/order/getOrderStatus"
            
            response = self.session.post(
                url,
                json=third_ids,
                headers=headers,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": data.get("code") == 200,
                    "data": data,
                    "message": data.get("msg", "Success")
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "data": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def generate_third_id(self, prefix: str = "PYEN") -> str:
        """Generate third party ID following Chinese API format"""
        now = datetime.now()
        date_str = now.strftime("%y%m%d")
        timestamp_suffix = str(int(time.time()))[-6:]
        return f"{prefix}{date_str}{timestamp_suffix}"
    
    @staticmethod
    def get_api_base_url():
        """Get the base URL for Chinese API"""
        return ChineseAPIConfig().base_url

# Singleton instance
_chinese_api_service = None

def get_chinese_api_service() -> ChineseAPIService:
    """Get singleton instance of Chinese API service"""
    global _chinese_api_service
    if _chinese_api_service is None:
        _chinese_api_service = ChineseAPIService()
    return _chinese_api_service