"""Chinese manufacturer API-related Pydantic models"""

from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict
import json
import re

class OrderStatusUpdateRequest(BaseModel):
    order_id: str
    status: Optional[str] = None
    equipment_id: Optional[str] = None
    queue_number: Optional[str] = None
    estimated_completion: Optional[str] = None
    chinese_order_id: Optional[str] = None
    notes: Optional[str] = None
    
    @field_validator('order_id')
    @classmethod
    def validate_order_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Order ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Order ID too long')
        return v.strip()
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return v
        valid_statuses = ['pending', 'printing', 'printed', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v
    
    @field_validator('equipment_id')
    @classmethod
    def validate_equipment_id(cls, v):
        if v is not None and len(v) > 100:
            raise ValueError('Equipment ID too long')
        return v
    
    @field_validator('queue_number')
    @classmethod
    def validate_queue_number(cls, v):
        if v and len(v) > 50:
            raise ValueError('Queue number too long')
        return v
    
    @field_validator('chinese_order_id')
    @classmethod
    def validate_chinese_order_id(cls, v):
        if v and len(v) > 100:
            raise ValueError('Chinese order ID too long')
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v and len(v) > 500:
            raise ValueError('Notes too long (max 500 characters)')
        return v

class PrintCommandRequest(BaseModel):
    order_id: str
    image_urls: List[str]
    phone_model: str
    customer_info: dict
    priority: Optional[int] = 1
    
    @field_validator('order_id')
    @classmethod
    def validate_order_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Order ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Order ID too long')
        return v.strip()
    
    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one image URL is required')
        if len(v) > 20:
            raise ValueError('Too many image URLs (max 20)')
        
        for url in v:
            if not url or len(url.strip()) == 0:
                raise ValueError('Image URL cannot be empty')
            if len(url) > 500:
                raise ValueError('Image URL too long')
            if not (url.startswith('http://') or url.startswith('https://')):
                raise ValueError('Image URL must start with http:// or https://')
        
        return [url.strip() for url in v]
    
    @field_validator('phone_model')
    @classmethod
    def validate_phone_model(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Phone model cannot be empty')
        if len(v) > 100:
            raise ValueError('Phone model name too long')
        return v.strip()
    
    @field_validator('customer_info')
    @classmethod
    def validate_customer_info(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Customer info must be a dictionary')
        if len(json.dumps(v)) > 2000:
            raise ValueError('Customer info too large')
        return v
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Priority must be between 1 and 10')
        return v

class ChinesePayStatusRequest(BaseModel):
    third_id: str
    status: int
    
    @field_validator('third_id')
    @classmethod
    def validate_third_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Third party payment ID cannot be empty')
        if len(v) > 200:
            raise ValueError('Third party payment ID too long')
        return v.strip()
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        # Chinese payment status: 1=waiting, 2=paying, 3=paid, 4=failed, 5=abnormal
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError('Status must be 1 (waiting), 2 (paying), 3 (paid), 4 (failed), or 5 (abnormal)')
        return v

class ChinesePaymentDataRequest(BaseModel):
    mobile_model_id: str
    device_id: str
    third_id: str
    pay_amount: float
    pay_type: int
    
    @field_validator('mobile_model_id')
    @classmethod
    def validate_mobile_model_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Mobile model ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Mobile model ID too long')
        return v.strip()
    
    @field_validator('device_id')
    @classmethod
    def validate_device_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Device ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Device ID too long')
        return v.strip()
    
    @field_validator('third_id')
    @classmethod
    def validate_third_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Third party payment ID cannot be empty')
        if len(v) > 50:
            raise ValueError('Third party payment ID too long')
        # Validate PYEN format: PYEN + yyMMdd + 6digits
        if not re.match(r'^PYEN\d{6}\d{6}$', v):
            raise ValueError('Third party payment ID must follow format: PYEN + yyMMdd + 6digits')
        return v.strip()
    
    @field_validator('pay_amount')
    @classmethod
    def validate_pay_amount(cls, v):
        if v is None or v <= 0:
            raise ValueError('Payment amount must be greater than 0')
        if v > 10000:  # Maximum £10,000 for safety
            raise ValueError('Payment amount too high')
        return round(float(v), 2)
    
    @field_validator('pay_type')
    @classmethod
    def validate_pay_type(cls, v):
        # Chinese payment types: 1=WeChat, 2=Alipay, 3=UnionPay, 4=Cash, 5=NAYAX, 6=Card, 7=On-site, 8=TikTok, 9=Meituan, 10=WeChat code, 11=Philippines, 12=UK online
        valid_types = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        if v not in valid_types:
            raise ValueError(f'Payment type must be one of: {valid_types}')
        return v

class ChineseOrderDataRequest(BaseModel):
    third_pay_id: str
    third_id: str
    mobile_model_id: str
    pic: str
    device_id: str
    mobile_shell_id: str
    
    @field_validator('third_pay_id')
    @classmethod
    def validate_third_pay_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Third party payment ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Third party payment ID too long')
        return v.strip()
    
    @field_validator('third_id')
    @classmethod
    def validate_third_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Third ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Third ID too long')
        return v.strip()
    
    @field_validator('mobile_model_id')
    @classmethod
    def validate_mobile_model_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Mobile model ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Mobile model ID too long')
        # Reject known test/hardcoded values
        test_values = ['MM020250224000010', 'UNKNOWN_MODEL', 'TEST_MODEL']
        if v.strip() in test_values:
            raise ValueError(f'Mobile model ID appears to be a test/hardcoded value: {v}')
        return v.strip()
    
    @field_validator('pic')
    @classmethod
    def validate_pic(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Image URL cannot be empty')
        if len(v) > 1000:
            raise ValueError('Image URL too long')
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Image URL must start with http:// or https://')
        return v.strip()
    
    @field_validator('device_id')
    @classmethod
    def validate_device_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Device ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Device ID too long')
        return v.strip()
    
    @field_validator('mobile_shell_id')
    @classmethod
    def validate_mobile_shell_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Mobile shell ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Mobile shell ID too long')
        # Reject known test/hardcoded values
        test_values = ['MS102503270003', 'DYNAMIC_SHELL', 'TEST_SHELL']
        if v.strip() in test_values:
            raise ValueError(f'Mobile shell ID appears to be a test/hardcoded value: {v}')
        return v.strip()