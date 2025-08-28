"""Helper utility functions"""

import time
from datetime import datetime
from sqlalchemy.orm import Session

def generate_third_id(prefix="PYEN"):
    """Generate third_id in Chinese API format: PREFIX + yyMMdd + 6digits
    Examples: 
    - PYEN250604000001 (for payments)
    - OREN250604000001 (for orders)
    
    Args:
        prefix (str): Prefix to use. Default "PYEN" for payments, use "OREN" for orders
    """
    # CRITICAL FIX: Use UTC timezone for consistent date generation to prevent date boundary issues
    from datetime import datetime, timezone
    current_date = datetime.now(timezone.utc)
    date_str = current_date.strftime("%y%m%d")
    
    # Generate 6-digit sequential number (using timestamp + random for uniqueness)
    timestamp_suffix = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
    
    # Ensure we have exactly 6 digits
    if len(timestamp_suffix) < 6:
        timestamp_suffix = timestamp_suffix.zfill(6)
    
    third_id = f"{prefix}{date_str}{timestamp_suffix}"
    print(f"Backend - Generated third_id (UTC): {third_id}")
    return third_id

def get_mobile_model_id(phone_model, db: Session):
    """Get mobile_model_id for Chinese API from PhoneModel
    Returns chinese_model_id if available, otherwise uses internal ID
    """
    if not phone_model:
        return "UNKNOWN_MODEL"
    
    # Try to use chinese_model_id first
    if phone_model.chinese_model_id and phone_model.chinese_model_id.strip():
        return phone_model.chinese_model_id.strip()
    
    # Fallback to internal ID
    return phone_model.id