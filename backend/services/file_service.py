"""File service for handling downloads and secure tokens"""

import time
import hmac
import hashlib
from backend.config.settings import UK_HOSTED_BASE_URL, JWT_SECRET_KEY, DEFAULT_TOKEN_EXPIRY_HOURS

def generate_uk_download_url(filename: str) -> str:
    """Generate UK-hosted download URL for Chinese partners"""
    return f"{UK_HOSTED_BASE_URL}/image/{filename}"

def generate_secure_download_token(filename: str, expiry_hours: int = DEFAULT_TOKEN_EXPIRY_HOURS) -> str:
    """Generate secure download token for image access"""
    # Use JWT secret as signing key
    secret_key = JWT_SECRET_KEY
    timestamp = str(int(time.time() + (expiry_hours * 3600)))  # Expiry timestamp
    
    # Create signature
    message = f"{filename}:{timestamp}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return f"{timestamp}:{signature}"