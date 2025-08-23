"""Chinese manufacturer payment API service with authentication and signature generation"""

import requests
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import time
import logging

from backend.config.settings import (
    CHINESE_API_BASE_URL, CHINESE_API_ACCOUNT, CHINESE_API_PASSWORD,
    CHINESE_API_SYSTEM_NAME, CHINESE_API_FIXED_KEY, 
    CHINESE_API_DEVICE_ID, CHINESE_API_TIMEOUT
)

# Set up logging
logger = logging.getLogger(__name__)

class ChinesePaymentAPIClient:
    """Client for Chinese manufacturer payment API with proper authentication and signature generation"""
    
    def __init__(self):
        self.base_url = CHINESE_API_BASE_URL
        self.account = CHINESE_API_ACCOUNT
        self.password = CHINESE_API_PASSWORD
        self.system_name = CHINESE_API_SYSTEM_NAME
        self.fixed_key = CHINESE_API_FIXED_KEY
        self.device_id = CHINESE_API_DEVICE_ID
        self.timeout = CHINESE_API_TIMEOUT
        
        self.token = None
        self.token_expires_at = None
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PimpMyCase-API/2.0.0'
        })

    def generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate MD5 signature for API request following Chinese API specification"""
        try:
            # Sort parameters by key
            sorted_params = dict(sorted(params.items()))
            
            # Concatenate values
            signature_string = ""
            for key in sorted(sorted_params.keys()):
                value = sorted_params[key]
                if value is not None:
                    signature_string += str(value)
            
            # Add system name and fixed key
            signature_string += self.system_name
            signature_string += self.fixed_key
            
            logger.debug(f"Signature string: {signature_string}")
            
            # Generate MD5 hash
            signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()
            logger.debug(f"Generated signature: {signature}")
            
            return signature
            
        except Exception as e:
            logger.error(f"Failed to generate signature: {str(e)}")
            raise

    def is_token_valid(self) -> bool:
        """Check if current token is valid and not expired"""
        if not self.token:
            return False
        
        if not self.token_expires_at:
            return True  # If no expiry set, assume it's valid for now
            
        return datetime.now(timezone.utc).timestamp() < self.token_expires_at

    def login(self) -> bool:
        """Login and get authentication token"""
        try:
            logger.info("Authenticating with Chinese API")
            
            login_data = {
                "account": self.account,
                "password": self.password
            }
            
            signature = self.generate_signature(login_data)
            
            headers = {
                "sign": signature,
                "req_source": "en"
            }
            
            response = self.session.post(
                f"{self.base_url}/user/login",
                json=login_data,
                headers=headers,
                timeout=self.timeout
            )
            
            logger.info(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Login response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if data.get("code") == 200:
                    self.token = data["data"]["token"]
                    # Set token expiry to 1 hour from now (Chinese API doesn't specify, so we assume)
                    self.token_expires_at = datetime.now(timezone.utc).timestamp() + 3600
                    logger.info(f"Login successful! Token: {self.token[:20]}...")
                    return True
                else:
                    logger.error(f"Login failed - API error: {data.get('code')} - {data.get('msg')}")
            else:
                logger.error(f"Login failed - HTTP status: {response.status_code}")
                logger.error(f"Response: {response.text}")
            
            return False
            
        except requests.RequestException as e:
            logger.error(f"Login request failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Login exception: {str(e)}")
            return False

    def ensure_authenticated(self) -> bool:
        """Ensure we have a valid authentication token"""
        if self.is_token_valid():
            return True
            
        return self.login()

    def send_payment_data(self, mobile_model_id: str, third_id: str, 
                         pay_amount: float, pay_type: int = 5, 
                         device_id: Optional[str] = None) -> Dict[str, Any]:
        """Send payment data to Chinese manufacturers for vending machine payment processing"""
        try:
            logger.info(f"=== CHINESE PAYMENT SERVICE START ===")
            logger.info(f"Target URL: {self.base_url}/order/payData") 
            logger.info(f"Payment details: third_id={third_id}, amount={pay_amount}, pay_type={pay_type}")
            logger.info(f"Mobile model ID: {mobile_model_id}")
            logger.info(f"Device ID: {device_id}")
            
            # Ensure we're authenticated
            logger.info("Checking authentication status...")
            auth_start = time.time()
            if not self.ensure_authenticated():
                logger.error("Authentication failed - cannot proceed with payment")
                return {
                    "msg": "Authentication failed",
                    "code": 500,
                    "data": {"id": "", "third_id": third_id}
                }
            
            auth_duration = time.time() - auth_start
            logger.info(f"Authentication successful in {auth_duration:.2f}s, token: {self.token[:20] if self.token else 'None'}...")
            
            # Use provided device_id or fall back to configured one
            effective_device_id = device_id or self.device_id
            if not effective_device_id:
                logger.error("No device_id provided and no default configured")
                return {
                    "msg": "Device ID is required",
                    "code": 400,
                    "data": {"id": "", "third_id": third_id}
                }
            
            payload = {
                "mobile_model_id": mobile_model_id,
                "device_id": effective_device_id,
                "third_id": third_id,
                "pay_amount": pay_amount,
                "pay_type": pay_type
            }
            
            logger.info(f"=== PAYLOAD TO CHINESE API ===")
            logger.info(f"Request payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            # Generate signature
            logger.info("Generating signature...")
            signature_start = time.time()
            signature = self.generate_signature(payload)
            signature_duration = time.time() - signature_start
            logger.info(f"Signature generated in {signature_duration:.3f}s: {signature}")
            
            headers = {
                "Authorization": self.token,
                "sign": signature,
                "req_source": "en",
                "Content-Type": "application/json",
                "User-Agent": "PimpMyCase-API/2.0.0"
            }
            
            logger.info(f"=== REQUEST HEADERS ===")
            # Log headers but mask sensitive data
            safe_headers = headers.copy()
            if safe_headers.get("Authorization"):
                safe_headers["Authorization"] = safe_headers["Authorization"][:20] + "..." if len(safe_headers["Authorization"]) > 20 else safe_headers["Authorization"]
            logger.info(f"Headers: {json.dumps(safe_headers, indent=2, ensure_ascii=False)}")
            
            # Make the request
            full_url = f"{self.base_url}/order/payData"
            logger.info(f"Making POST request to: {full_url}")
            request_start = time.time()
            
            response = self.session.post(
                full_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            request_duration = time.time() - request_start
            logger.info(f"HTTP request completed in {request_duration:.2f}s")
            
            logger.info(f"=== CHINESE API HTTP RESPONSE ===")
            logger.info(f"HTTP Status: {response.status_code} {response.reason}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"Response body: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # Check Chinese API response code
                    if data.get("code") == 200:
                        payment_id = data.get('data', {}).get('id', 'N/A')
                        logger.info(f"SUCCESS: Payment data sent successfully!")
                        logger.info(f"Chinese Payment ID: {payment_id}")
                        logger.info(f"Third ID: {third_id}")
                    else:
                        logger.error(f"Chinese API returned error code: {data.get('code')}")
                        logger.error(f"Error message: {data.get('msg', 'No message provided')}")
                    
                    logger.info(f"=== CHINESE PAYMENT SERVICE END (SUCCESS) ===")
                    return data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.error(f"Raw response text: {response.text[:1000]}")
                    return {
                        "msg": f"Invalid JSON response from Chinese API",
                        "code": 502,
                        "data": {"id": "", "third_id": third_id}
                    }
            else:
                logger.error(f"HTTP request failed with status: {response.status_code}")
                logger.error(f"Response reason: {response.reason}")
                
                error_body = "No response body"
                try:
                    error_body = response.text
                    logger.error(f"Error response body: {error_body[:1000]}")
                except Exception as e:
                    logger.error(f"Could not read error response: {e}")
                
                logger.error(f"=== CHINESE PAYMENT SERVICE END (HTTP ERROR) ===")
                return {
                    "msg": f"HTTP {response.status_code}: {error_body}",
                    "code": response.status_code,
                    "data": {"id": "", "third_id": third_id},
                    "http_error": True
                }
                
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout after {self.timeout}s: {str(e)}")
            logger.error(f"=== CHINESE PAYMENT SERVICE END (TIMEOUT) ===")
            return {
                "msg": f"Request timeout after {self.timeout}s",
                "code": 504,
                "data": {"id": "", "third_id": third_id},
                "timeout": True
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Chinese API: {str(e)}")
            logger.error(f"Target URL: {self.base_url}/order/payData")
            logger.error(f"=== CHINESE PAYMENT SERVICE END (CONNECTION ERROR) ===")
            return {
                "msg": f"Connection failed to Chinese API: {str(e)}",
                "code": 503,
                "data": {"id": "", "third_id": third_id},
                "connection_error": True
            }
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            logger.error(f"=== CHINESE PAYMENT SERVICE END (REQUEST ERROR) ===")
            return {
                "msg": f"Request failed: {str(e)}",
                "code": 500,
                "data": {"id": "", "third_id": third_id},
                "request_error": True
            }
        except Exception as e:
            logger.error(f"Unexpected error in payment service: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.error(f"=== CHINESE PAYMENT SERVICE END (UNEXPECTED ERROR) ===")
            return {
                "msg": f"Unexpected error: {str(e)}",
                "code": 500,
                "data": {"id": "", "third_id": third_id},
                "unexpected_error": True
            }

    def get_brand_list(self) -> Dict[str, Any]:
        """Get brand list from Chinese API"""
        try:
            logger.info("Fetching brand list from Chinese API")
            
            # Ensure we're authenticated
            if not self.ensure_authenticated():
                return {
                    "success": False,
                    "message": "Authentication failed",
                    "brands": []
                }
            
            # Empty payload for brand list
            payload = {}
            signature = self.generate_signature(payload)
            
            headers = {
                "Authorization": self.token,
                "sign": signature,
                "req_source": "en"
            }
            
            response = self.session.post(
                f"{self.base_url}/brand/list",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            logger.info(f"Brand list response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Brand list response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if data.get("code") == 200:
                    brands = data.get("data", [])
                    logger.info(f"Successfully fetched {len(brands)} brands")
                    return {
                        "success": True,
                        "brands": brands,
                        "total_brands": len(brands)
                    }
                else:
                    logger.warning(f"Brand list API returned error: {data.get('code')} - {data.get('msg')}")
                    return {
                        "success": False,
                        "message": data.get('msg', 'Unknown error'),
                        "brands": []
                    }
            else:
                error_msg = f"Brand list failed - HTTP {response.status_code}"
                logger.error(f"{error_msg}: {response.text}")
                return {
                    "success": False,
                    "message": error_msg,
                    "brands": []
                }
                
        except requests.RequestException as e:
            error_msg = f"Brand list request failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "brands": []
            }
        except Exception as e:
            error_msg = f"Brand list exception: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "brands": []
            }

    def get_stock_list(self, device_id: str, brand_id: str) -> Dict[str, Any]:
        """Get stock list for a specific brand and device from Chinese API"""
        try:
            logger.info(f"Fetching stock list from Chinese API - device_id: {device_id}, brand_id: {brand_id}")
            
            # Ensure we're authenticated
            if not self.ensure_authenticated():
                return {
                    "success": False,
                    "message": "Authentication failed",
                    "stock_items": []
                }
            
            # Payload for stock list
            payload = {
                "device_id": device_id,
                "brand_id": brand_id
            }
            
            signature = self.generate_signature(payload)
            
            headers = {
                "Authorization": self.token,
                "sign": signature,
                "req_source": "en"
            }
            
            response = self.session.post(
                f"{self.base_url}/stock/list",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            logger.info(f"Stock list response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Stock list response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if data.get("code") == 200:
                    stock_items = data.get("data", [])
                    logger.info(f"Successfully fetched {len(stock_items)} stock items for brand {brand_id}")
                    return {
                        "success": True,
                        "stock_items": stock_items,
                        "total_items": len(stock_items),
                        "device_id": device_id,
                        "brand_id": brand_id
                    }
                else:
                    logger.warning(f"Stock list API returned error: {data.get('code')} - {data.get('msg')}")
                    return {
                        "success": False,
                        "message": data.get('msg', 'Unknown error'),
                        "stock_items": []
                    }
            else:
                error_msg = f"Stock list failed - HTTP {response.status_code}"
                logger.error(f"{error_msg}: {response.text}")
                return {
                    "success": False,
                    "message": error_msg,
                    "stock_items": []
                }
                
        except requests.RequestException as e:
            error_msg = f"Stock list request failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "stock_items": []
            }
        except Exception as e:
            error_msg = f"Stock list exception: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "stock_items": []
            }

    def send_payment_status(self, third_id: str, status: int, pay_amount: float = None) -> Dict[str, Any]:
        """Send payment status notification to Chinese manufacturers after payment completion"""
        try:
            logger.info(f"=== CHINESE PAYMENT STATUS NOTIFICATION START ===")
            logger.info(f"Target URL: {self.base_url}/order/payStatus")
            logger.info(f"Payment status details: third_id={third_id}, status={status}, amount={pay_amount}")
            
            # Ensure we're authenticated
            logger.info("Checking authentication status...")
            if not self.ensure_authenticated():
                logger.error("Authentication failed - cannot proceed with payment status")
                return {
                    "msg": "Authentication failed",
                    "code": 500,
                    "data": {"third_id": third_id, "status": status}
                }
            
            # Prepare payload for payment status notification
            payload = {
                "third_id": third_id,
                "status": status
            }
            
            # Add amount if provided
            if pay_amount is not None:
                payload["pay_amount"] = pay_amount
            
            logger.info(f"=== PAYMENT STATUS PAYLOAD ===")
            logger.info(f"Request payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            # Generate signature
            signature = self.generate_signature(payload)
            
            headers = {
                "Authorization": self.token,
                "sign": signature,
                "req_source": "en",
                "Content-Type": "application/json",
                "User-Agent": "PimpMyCase-API/2.0.0"
            }
            
            # Make the request
            full_url = f"{self.base_url}/order/payStatus"
            logger.info(f"Making POST request to: {full_url}")
            request_start = time.time()
            
            response = self.session.post(
                full_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            request_duration = time.time() - request_start
            logger.info(f"Payment status request completed in {request_duration:.2f}s")
            
            logger.info(f"=== CHINESE API PAYMENT STATUS RESPONSE ===")
            logger.info(f"HTTP Status: {response.status_code} {response.reason}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"Response body: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if data.get("code") == 200:
                        logger.info(f"SUCCESS: Payment status sent successfully!")
                    else:
                        logger.error(f"Chinese API returned error code: {data.get('code')}")
                        logger.error(f"Error message: {data.get('msg', 'No message provided')}")
                    
                    logger.info(f"=== CHINESE PAYMENT STATUS NOTIFICATION END (SUCCESS) ===")
                    return data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    return {
                        "msg": f"Invalid JSON response from Chinese API",
                        "code": 502,
                        "data": {"third_id": third_id, "status": status}
                    }
            else:
                logger.error(f"HTTP request failed with status: {response.status_code}")
                error_body = response.text if response.text else "No response body"
                logger.error(f"Error response body: {error_body[:1000]}")
                
                logger.error(f"=== CHINESE PAYMENT STATUS NOTIFICATION END (HTTP ERROR) ===")
                return {
                    "msg": f"HTTP {response.status_code}: {error_body}",
                    "code": response.status_code,
                    "data": {"third_id": third_id, "status": status}
                }
                
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout after {self.timeout}s: {str(e)}")
            return {
                "msg": f"Request timeout after {self.timeout}s",
                "code": 504,
                "data": {"third_id": third_id, "status": status}
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Chinese API: {str(e)}")
            return {
                "msg": f"Connection failed to Chinese API: {str(e)}",
                "code": 503,
                "data": {"third_id": third_id, "status": status}
            }
        except Exception as e:
            logger.error(f"Unexpected error in payment status service: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "msg": f"Unexpected error: {str(e)}",
                "code": 500,
                "data": {"third_id": third_id, "status": status}
            }

    def send_order_data(self, third_pay_id: str, third_id: str, mobile_model_id: str, 
                       pic: str, device_id: str) -> Dict[str, Any]:
        """Send order data to Chinese manufacturers for printing"""
        try:
            logger.info(f"=== CHINESE ORDER DATA SUBMISSION START ===")
            logger.info(f"Target URL: {self.base_url}/order/orderData")
            logger.info(f"Order details: third_pay_id={third_pay_id}, third_id={third_id}")
            logger.info(f"Mobile model ID: {mobile_model_id}, device_id: {device_id}")
            logger.info(f"Design image URL: {pic}")
            
            # CRITICAL FIX: Wait 3 seconds to allow Chinese API to process payment internally
            # This prevents "Payment information does not exist" error
            import time
            logger.info("Waiting 3 seconds for Chinese API to process payment before sending order data...")
            time.sleep(3)
            logger.info("3-second delay completed, proceeding with order data submission")
            
            # Ensure we're authenticated
            if not self.ensure_authenticated():
                logger.error("Authentication failed - cannot proceed with order submission")
                return {
                    "msg": "Authentication failed",
                    "code": 500,
                    "data": {"third_pay_id": third_pay_id, "third_id": third_id}
                }
            
            payload = {
                "third_pay_id": third_pay_id,
                "third_id": third_id,
                "mobile_model_id": mobile_model_id,
                "pic": pic,
                "device_id": device_id
            }
            
            logger.info(f"=== ORDER DATA PAYLOAD ===")
            logger.info(f"Request payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            # Generate signature
            signature = self.generate_signature(payload)
            
            headers = {
                "Authorization": self.token,
                "sign": signature,
                "req_source": "en",
                "Content-Type": "application/json",
                "User-Agent": "PimpMyCase-API/2.0.0"
            }
            
            # Make the request
            full_url = f"{self.base_url}/order/orderData"
            logger.info(f"Making POST request to: {full_url}")
            request_start = time.time()
            
            response = self.session.post(
                full_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            request_duration = time.time() - request_start
            logger.info(f"Order data request completed in {request_duration:.2f}s")
            
            logger.info(f"=== CHINESE API ORDER DATA RESPONSE ===")
            logger.info(f"HTTP Status: {response.status_code} {response.reason}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"Response body: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if data.get("code") == 200:
                        order_id = data.get('data', {}).get('id', 'N/A')
                        queue_no = data.get('data', {}).get('queue_no', 'N/A')
                        logger.info(f"SUCCESS: Order data sent successfully!")
                        logger.info(f"Chinese Order ID: {order_id}")
                        logger.info(f"Queue Number: {queue_no}")
                    else:
                        logger.error(f"Chinese API returned error code: {data.get('code')}")
                        logger.error(f"Error message: {data.get('msg', 'No message provided')}")
                    
                    logger.info(f"=== CHINESE ORDER DATA SUBMISSION END (SUCCESS) ===")
                    return data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    return {
                        "msg": f"Invalid JSON response from Chinese API",
                        "code": 502,
                        "data": {"third_pay_id": third_pay_id, "third_id": third_id}
                    }
            else:
                logger.error(f"HTTP request failed with status: {response.status_code}")
                error_body = response.text if response.text else "No response body"
                logger.error(f"Error response body: {error_body[:1000]}")
                
                logger.error(f"=== CHINESE ORDER DATA SUBMISSION END (HTTP ERROR) ===")
                return {
                    "msg": f"HTTP {response.status_code}: {error_body}",
                    "code": response.status_code,
                    "data": {"third_pay_id": third_pay_id, "third_id": third_id}
                }
                
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout after {self.timeout}s: {str(e)}")
            return {
                "msg": f"Request timeout after {self.timeout}s",
                "code": 504,
                "data": {"third_pay_id": third_pay_id, "third_id": third_id}
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to Chinese API: {str(e)}")
            return {
                "msg": f"Connection failed to Chinese API: {str(e)}",
                "code": 503,
                "data": {"third_pay_id": third_pay_id, "third_id": third_id}
            }
        except Exception as e:
            logger.error(f"Unexpected error in order data service: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "msg": f"Unexpected error: {str(e)}",
                "code": 500,
                "data": {"third_pay_id": third_pay_id, "third_id": third_id}
            }

    def test_connection(self) -> Dict[str, Any]:
        """Test connection and authentication with Chinese API"""
        try:
            if self.ensure_authenticated():
                return {
                    "success": True,
                    "message": "Chinese API connection successful",
                    "token": self.token[:20] + "..." if self.token else None,
                    "base_url": self.base_url,
                    "device_id": self.device_id
                }
            else:
                return {
                    "success": False,
                    "message": "Authentication failed",
                    "base_url": self.base_url
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection test failed: {str(e)}",
                "base_url": self.base_url
            }

# Singleton instance
_chinese_client = None

def get_chinese_payment_client() -> ChinesePaymentAPIClient:
    """Get singleton instance of Chinese payment API client"""
    global _chinese_client
    if _chinese_client is None:
        _chinese_client = ChinesePaymentAPIClient()
    return _chinese_client

def send_payment_to_chinese_api(mobile_model_id: str, device_id: str, third_id: str, 
                               pay_amount: float, pay_type: int = 5) -> Dict[str, Any]:
    """Convenience function to send payment data to Chinese API"""
    client = get_chinese_payment_client()
    return client.send_payment_data(
        mobile_model_id=mobile_model_id,
        third_id=third_id, 
        pay_amount=pay_amount,
        pay_type=pay_type,
        device_id=device_id
    )

def test_chinese_api_connection() -> Dict[str, Any]:
    """Convenience function to test Chinese API connection"""
    client = get_chinese_payment_client()
    return client.test_connection()

def get_chinese_brands() -> Dict[str, Any]:
    """Convenience function to get brand list from Chinese API"""
    client = get_chinese_payment_client()
    return client.get_brand_list()

def get_chinese_stock(device_id: str, brand_id: str) -> Dict[str, Any]:
    """Convenience function to get stock list from Chinese API"""
    client = get_chinese_payment_client()
    return client.get_stock_list(device_id, brand_id)

def send_payment_status_to_chinese_api(third_id: str, status: int, pay_amount: float = None) -> Dict[str, Any]:
    """Convenience function to send payment status to Chinese API"""
    client = get_chinese_payment_client()
    return client.send_payment_status(third_id=third_id, status=status, pay_amount=pay_amount)

def send_order_data_to_chinese_api(third_pay_id: str, third_id: str, mobile_model_id: str, 
                                  pic: str, device_id: str) -> Dict[str, Any]:
    """Convenience function to send order data to Chinese API"""
    client = get_chinese_payment_client()
    return client.send_order_data(
        third_pay_id=third_pay_id,
        third_id=third_id,
        mobile_model_id=mobile_model_id,
        pic=pic,
        device_id=device_id
    )