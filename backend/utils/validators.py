"""Custom validation utilities"""

import re
from typing import Any, Dict

def validate_pyen_format(third_id: str) -> bool:
    """Validate PYEN format: PYEN + yyMMdd + 6digits"""
    return bool(re.match(r'^PYEN\d{6}\d{6}$', third_id))

def validate_json_size(data: Dict[str, Any], max_size: int = 2000) -> bool:
    """Validate that JSON data doesn't exceed size limit"""
    import json
    return len(json.dumps(data)) <= max_size

def validate_url_format(url: str) -> bool:
    """Validate basic URL format"""
    return url.startswith('http://') or url.startswith('https://')

def validate_payment_amount(amount: float, max_amount: float = 10000) -> bool:
    """Validate payment amount"""
    return amount is not None and 0 < amount <= max_amount