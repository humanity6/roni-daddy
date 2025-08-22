"""File service for handling downloads and secure tokens"""

import time
import hmac
import hashlib
import logging
from typing import Optional, Dict, Any
from backend.config.settings import UK_HOSTED_BASE_URL, JWT_SECRET_KEY, DEFAULT_TOKEN_EXPIRY_HOURS

logger = logging.getLogger(__name__)

# Partner types for different access levels
PARTNER_TYPES = {
    "chinese_manufacturing": {
        "default_expiry_hours": 48,
        "max_expiry_hours": 72,
        "description": "Chinese manufacturing partners"
    },
    "end_user": {
        "default_expiry_hours": 1,
        "max_expiry_hours": 4,
        "description": "End user access"
    },
    "admin": {
        "default_expiry_hours": 24,
        "max_expiry_hours": 168,  # 7 days
        "description": "Administrative access"
    }
}

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
    
    logger.info(f"Generated secure token for {filename} with {expiry_hours}h expiry")
    return f"{timestamp}:{signature}"

def generate_partner_specific_token(filename: str, partner_type: str = "end_user", custom_expiry_hours: Optional[int] = None) -> str:
    """Generate secure download token with partner-specific settings"""
    if partner_type not in PARTNER_TYPES:
        logger.warning(f"Unknown partner type '{partner_type}', defaulting to 'end_user'")
        partner_type = "end_user"
    
    partner_config = PARTNER_TYPES[partner_type]
    
    # Determine expiry hours
    if custom_expiry_hours:
        # Validate custom expiry against partner max
        expiry_hours = min(custom_expiry_hours, partner_config["max_expiry_hours"])
        if custom_expiry_hours > partner_config["max_expiry_hours"]:
            logger.warning(f"Custom expiry {custom_expiry_hours}h exceeds max {partner_config['max_expiry_hours']}h for {partner_type}, using max")
    else:
        expiry_hours = partner_config["default_expiry_hours"]
    
    # Generate token with partner prefix for identification
    secret_key = JWT_SECRET_KEY
    timestamp = str(int(time.time() + (expiry_hours * 3600)))
    
    # Include partner type in the signature for validation
    message = f"{filename}:{timestamp}:{partner_type}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    token = f"{timestamp}:{partner_type}:{signature}"
    logger.info(f"Generated {partner_type} token for {filename} with {expiry_hours}h expiry")
    
    return token

def validate_secure_token(token: str, filename: str, allow_partner_types: Optional[list] = None) -> Dict[str, Any]:
    """Validate secure download token and return validation info"""
    try:
        if not token or not filename:
            return {"valid": False, "error": "Missing token or filename"}
        
        # Check if this is a partner-specific token (contains partner type)
        parts = token.split(':')
        if len(parts) == 3:
            # Partner-specific token format: timestamp:partner_type:signature
            timestamp_str, partner_type, signature = parts
            
            # Validate partner type
            if partner_type not in PARTNER_TYPES:
                logger.warning(f"Token validation failed - invalid partner type: {partner_type}")
                return {"valid": False, "error": "Invalid partner type"}
            
            # Check if partner type is allowed
            if allow_partner_types and partner_type not in allow_partner_types:
                logger.warning(f"Token validation failed - partner type {partner_type} not allowed")
                return {"valid": False, "error": "Partner type not allowed"}
            
            # Recreate message for validation
            message = f"{filename}:{timestamp_str}:{partner_type}"
            
        elif len(parts) == 2:
            # Standard token format: timestamp:signature
            timestamp_str, signature = parts
            partner_type = "standard"
            message = f"{filename}:{timestamp_str}"
            
        else:
            logger.warning(f"Token validation failed - invalid format for {filename}")
            return {"valid": False, "error": "Invalid token format"}
        
        # Check expiry
        timestamp = int(timestamp_str)
        current_time = int(time.time())
        
        if current_time > timestamp:
            logger.warning(f"Token validation failed - expired token for {filename}")
            return {"valid": False, "error": "Token expired"}
        
        # Verify signature
        expected_signature = hmac.new(
            JWT_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning(f"Token validation failed - invalid signature for {filename}")
            return {"valid": False, "error": "Invalid token signature"}
        
        # Token is valid
        time_remaining = timestamp - current_time
        logger.info(f"Token validated successfully for {filename}, partner: {partner_type}, time remaining: {time_remaining}s")
        
        return {
            "valid": True,
            "partner_type": partner_type,
            "expires_at": timestamp,
            "time_remaining_seconds": time_remaining,
            "filename": filename
        }
        
    except (ValueError, TypeError) as e:
        logger.error(f"Token validation error for {filename}: {str(e)}")
        return {"valid": False, "error": f"Token validation error: {str(e)}"}

def generate_secure_image_url(filename: str, partner_type: str = "end_user", custom_expiry_hours: Optional[int] = None, base_url: str = None) -> str:
    """Generate complete secure image URL with token"""
    if not base_url:
        base_url = "https://pimpmycase.onrender.com"
    
    # Generate appropriate token
    if partner_type == "standard":
        token = generate_secure_download_token(filename, custom_expiry_hours or DEFAULT_TOKEN_EXPIRY_HOURS)
    else:
        token = generate_partner_specific_token(filename, partner_type, custom_expiry_hours)
    
    secure_url = f"{base_url}/image/{filename}?token={token}"
    logger.info(f"Generated secure URL for {filename}, partner: {partner_type}")
    
    return secure_url

def refresh_token(old_token: str, filename: str, additional_hours: int = 1) -> Optional[str]:
    """Refresh an existing token by extending its expiry"""
    validation = validate_secure_token(old_token, filename)
    
    if not validation["valid"]:
        logger.warning(f"Cannot refresh invalid token for {filename}")
        return None
    
    partner_type = validation.get("partner_type", "end_user")
    partner_config = PARTNER_TYPES.get(partner_type, PARTNER_TYPES["end_user"])
    
    # Don't allow refresh beyond max expiry
    new_expiry_hours = min(additional_hours, partner_config["max_expiry_hours"])
    
    if partner_type == "standard":
        return generate_secure_download_token(filename, new_expiry_hours)
    else:
        return generate_partner_specific_token(filename, partner_type, new_expiry_hours)