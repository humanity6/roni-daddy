"""
Security middleware and validation for PimpMyCase API
Provides rate limiting, session validation, and security checks
"""

import time
import hashlib
import hmac
import re
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from collections import defaultdict
import json
import ipaddress

class SecurityManager:
    """Centralized security management for API endpoints"""
    
    def __init__(self):
        # Rate limiting storage (in production, use Redis)
        self.rate_limit_storage: Dict[str, List[float]] = defaultdict(list)
        self.failed_attempts: Dict[str, int] = defaultdict(int)
        self.blocked_ips: Dict[str, datetime] = {}
        
        # Session security tracking
        self.session_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.machine_sessions: Dict[str, int] = defaultdict(int)
        
        # Valid session ID pattern (supports both upper and lowercase)
        self.session_id_pattern = re.compile(r'^[A-Za-z0-9_]+_\d{8}_\d{6}_[A-Fa-f0-9]{8}$')
        
    def validate_session_id_format(self, session_id: str) -> bool:
        """Validate session ID follows expected format with relaxed validation"""
        if not session_id or len(session_id) > 200:
            return False
        
        # Relaxed validation for all users to handle format variations
        # Strict checks first - these should always fail
        if '?' in session_id or '&' in session_id or '=' in session_id:
            return False
        
        # Allow both uppercase and lowercase characters for flexibility
        # (Removed case sensitivity restriction to support Chinese partners)
        
        # Split into parts for detailed validation
        parts = session_id.split('_')
        if len(parts) != 4:
            return False
        
        machine_id, date_part, time_part, random_part = parts
        
        # Validate each part
        if not re.match(r'^[A-Za-z0-9-]+$', machine_id):  # Machine ID: alphanumeric and hyphens (both cases)
            return False
        
        if len(date_part) not in [7, 8] or not date_part.isdigit():  # Date: 7 or 8 digits
            return False
        
        if len(time_part) != 6 or not time_part.isdigit():  # Time: exactly 6 digits
            return False
        
        if len(random_part) < 6 or len(random_part) > 8 or not re.match(r'^[A-Za-z0-9]+$', random_part):
            return False
        
        return True
    
    def validate_machine_id(self, machine_id: str) -> bool:
        """Validate machine ID format"""
        if not machine_id or len(machine_id) > 50:
            return False
        # Allow alphanumeric, underscores, hyphens
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', machine_id))
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in case of multiple proxies
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if hasattr(request.client, 'host'):
            return request.client.host
        
        return "unknown"
    
    def is_rate_limited(self, identifier: str, max_requests: int = 100, window_minutes: int = 1) -> bool:
        """Check if identifier is rate limited - RELAXED LIMITS FOR CHINESE PARTNERS"""
        
        now = time.time()
        window_start = now - (window_minutes * 60)
        
        # Clean old entries
        self.rate_limit_storage[identifier] = [
            timestamp for timestamp in self.rate_limit_storage[identifier] 
            if timestamp > window_start
        ]
        
        # Check if limit exceeded (much higher limits now)
        if len(self.rate_limit_storage[identifier]) >= max_requests:
            return True
        
        # Add current request
        self.rate_limit_storage[identifier].append(now)
        return False
    
    def get_retry_delay(self, identifier: str, attempt_count: int = 1) -> dict:
        """Calculate retry delay with exponential backoff for rate-limited requests"""
        # Base delay starts at 1 second, doubles with each attempt, max 30 seconds
        base_delay = min(1 * (2 ** (attempt_count - 1)), 30)
        
        # Add jitter to prevent thundering herd
        import random
        jitter = random.uniform(0.1, 0.5)
        total_delay = base_delay + jitter
        
        return {
            "retry_after_seconds": total_delay,
            "attempt_count": attempt_count,
            "message": f"Request rate limited. Please wait {total_delay:.1f} seconds before retrying."
        }
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is temporarily blocked"""
        if ip_address in self.blocked_ips:
            if datetime.utcnow() < self.blocked_ips[ip_address]:
                return True
            else:
                # Block expired, remove it
                del self.blocked_ips[ip_address]
        return False
    
    def record_failed_attempt(self, identifier: str, block_duration_minutes: int = 10):
        """Record failed attempt and block if threshold exceeded"""
        self.failed_attempts[identifier] += 1
        
        # Block after 5 failed attempts
        if self.failed_attempts[identifier] >= 5:
            self.blocked_ips[identifier] = datetime.utcnow() + timedelta(minutes=block_duration_minutes)
            # Reset counter
            self.failed_attempts[identifier] = 0
    
    def reset_failed_attempts(self, identifier: str):
        """Reset failed attempts counter for identifier"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
    
    def validate_payment_amount(self, amount: float, expected_range: tuple = (0.01, 500.0)) -> bool:
        """Validate payment amount is within reasonable range (including test prices)"""
        if not isinstance(amount, (int, float)):
            return False
        return expected_range[0] <= amount <= expected_range[1]
    
    def sanitize_string_input(self, input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input to prevent injection attacks"""
        if not input_str:
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(input_str))
        
        # Truncate to max length
        sanitized = sanitized[:max_length]
        
        # Basic HTML/script tag removal (basic XSS prevention)
        sanitized = re.sub(r'<[^>]*>', '', sanitized)
        
        return sanitized.strip()
    
    def validate_session_activity(self, session_id: str, max_requests_per_minute: int = 20) -> bool:
        """Validate session activity to prevent abuse"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        self.session_attempts[session_id] = [
            timestamp for timestamp in self.session_attempts[session_id]
            if timestamp > minute_ago
        ]
        
        # Check if limit exceeded
        if len(self.session_attempts[session_id]) >= max_requests_per_minute:
            return False
        
        # Add current request
        self.session_attempts[session_id].append(now)
        return True
    
    def validate_machine_session_limit(self, machine_id: str, max_concurrent: int = 5, db_session=None) -> bool:
        """Validate machine doesn't exceed concurrent session limit with automatic cleanup"""
        # Clean up expired sessions if database session provided
        if db_session:
            self._cleanup_expired_sessions_for_machine(machine_id, db_session)
            
            # Periodically reconcile session counts (every 50th request to avoid overhead)
            import random
            if random.randint(1, 50) == 1:
                self.reconcile_machine_session_counts(db_session)
        
        return self.machine_sessions[machine_id] < max_concurrent
    
    def increment_machine_sessions(self, machine_id: str):
        """Increment active session count for machine"""
        self.machine_sessions[machine_id] += 1
    
    def decrement_machine_sessions(self, machine_id: str):
        """Decrement active session count for machine"""
        if self.machine_sessions[machine_id] > 0:
            self.machine_sessions[machine_id] -= 1
    
    def _cleanup_expired_sessions_for_machine(self, machine_id: str, db_session):
        """Clean up expired sessions for a specific machine and update session count"""
        try:
            from models import VendingMachineSession
            from datetime import datetime, timezone
            
            # Find expired sessions for this machine
            expired_sessions = db_session.query(VendingMachineSession).filter(
                VendingMachineSession.machine_id == machine_id,
                VendingMachineSession.status == "active",
                VendingMachineSession.expires_at < datetime.now(timezone.utc)
            ).all()
            
            # Update their status and decrement session count
            cleanup_count = 0
            for session in expired_sessions:
                session.status = "expired"
                cleanup_count += 1
            
            if cleanup_count > 0:
                # Adjust in-memory session count
                current_count = self.machine_sessions[machine_id]
                new_count = max(0, current_count - cleanup_count)
                self.machine_sessions[machine_id] = new_count
                
                db_session.commit()
                print(f"Cleaned up {cleanup_count} expired sessions for machine {machine_id}, session count: {current_count} -> {new_count}")
                
        except Exception as e:
            print(f"Error during session cleanup for machine {machine_id}: {str(e)}")
            # Don't let cleanup errors break the validation
    
    def reconcile_machine_session_counts(self, db_session):
        """Reconcile in-memory session counts with actual database state"""
        try:
            from models import VendingMachineSession
            from datetime import datetime, timezone
            from collections import defaultdict
            
            # Get actual active session counts from database
            active_sessions = db_session.query(VendingMachineSession).filter(
                VendingMachineSession.status == "active",
                VendingMachineSession.expires_at > datetime.now(timezone.utc)
            ).all()
            
            # Count sessions by machine
            actual_counts = defaultdict(int)
            for session in active_sessions:
                actual_counts[session.machine_id] += 1
            
            # Update in-memory counts to match reality
            reconciled_machines = []
            for machine_id in list(self.machine_sessions.keys()):
                old_count = self.machine_sessions[machine_id]
                new_count = actual_counts[machine_id]
                
                if old_count != new_count:
                    self.machine_sessions[machine_id] = new_count
                    reconciled_machines.append(f"{machine_id}: {old_count} -> {new_count}")
            
            # Add any machines that have sessions in DB but not in memory
            for machine_id, count in actual_counts.items():
                if machine_id not in self.machine_sessions:
                    self.machine_sessions[machine_id] = count
                    reconciled_machines.append(f"{machine_id}: 0 -> {count} (new)")
            
            if reconciled_machines:
                print(f"Reconciled session counts: {reconciled_machines}")
                
        except Exception as e:
            print(f"Error during session count reconciliation: {str(e)}")
    
    def generate_session_token(self, session_id: str, secret_key: str) -> str:
        """Generate signed token for session validation"""
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"
        signature = hmac.new(
            secret_key.encode(), 
            message.encode(), 
            hashlib.sha256
        ).hexdigest()
        return f"{message}:{signature}"
    
    def validate_session_token(self, token: str, secret_key: str, max_age_seconds: int = 3600) -> Optional[str]:
        """Validate signed session token and return session_id if valid"""
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return None
            
            session_id, timestamp_str, signature = parts
            timestamp = int(timestamp_str)
            
            # Check if token is too old
            if time.time() - timestamp > max_age_seconds:
                return None
            
            # Verify signature
            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return session_id
            
        except (ValueError, IndexError):
            pass
        
        return None
    
    def validate_json_size(self, data: Any, max_size_kb: int = 500) -> bool:
        """Validate JSON payload size"""
        try:
            json_str = json.dumps(data)
            size_kb = len(json_str.encode('utf-8')) / 1024
            return size_kb <= max_size_kb
        except:
            return False
    
    def is_valid_ip_address(self, ip_str: str) -> bool:
        """Validate IP address format"""
        if not ip_str or ip_str == "unknown":
            return True  # Allow unknown IPs
        
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
    

# Global security manager instance
security_manager = SecurityManager()

def validate_session_security(request: Request, session_id: str) -> Dict[str, Any]:
    """Comprehensive session security validation with relaxed security for all users"""
    client_ip = security_manager.get_client_ip(request)
    
    # Basic validations with relaxed format checking
    if not security_manager.validate_session_id_format(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format - use format: MACHINE_ID_YYYYMMDD_HHMMSS_RANDOM (e.g., VM001_20250729_143022_A1B2C3 or 10HKNTDOH2BA_20250801_180922_A1B2C3A1)")
    
    if not security_manager.is_valid_ip_address(client_ip):
        raise HTTPException(status_code=400, detail="Invalid IP address")
    
    # Apply relaxed security checks for all users
    # Note: Most restrictive security checks are now skipped for all users
    
    return {
        "client_ip": client_ip,
        "validated": True,
        "security_level": "relaxed",
        "timestamp": datetime.utcnow().isoformat()
    }

def validate_machine_security(request: Request, machine_id: str) -> Dict[str, Any]:
    """Comprehensive machine security validation"""
    client_ip = security_manager.get_client_ip(request)
    
    # Basic validations
    if not security_manager.validate_machine_id(machine_id):
        raise HTTPException(status_code=400, detail="Invalid machine ID format")
    
    # Security checks
    if security_manager.is_ip_blocked(client_ip):
        raise HTTPException(status_code=429, detail="IP address temporarily blocked")
    
    if security_manager.is_rate_limited(f"machine:{machine_id}", max_requests=10, window_minutes=1):
        raise HTTPException(status_code=429, detail="Machine rate limit exceeded")
    
    if not security_manager.validate_machine_session_limit(machine_id):
        raise HTTPException(status_code=429, detail="Machine session limit exceeded")
    
    return {
        "client_ip": client_ip,
        "machine_id": machine_id,
        "validated": True,
        "timestamp": datetime.utcnow().isoformat()
    }

def validate_payment_security(request: Request, amount: float, session_id: str) -> Dict[str, Any]:
    """Comprehensive payment security validation"""
    client_ip = security_manager.get_client_ip(request)
    
    # Payment amount validation
    if not security_manager.validate_payment_amount(amount):
        raise HTTPException(status_code=400, detail="Invalid payment amount")
    
    # Session security check
    validate_session_security(request, session_id)
    
    return {
        "client_ip": client_ip,
        "amount": amount,
        "validated": True,
        "timestamp": datetime.utcnow().isoformat()
    }

def validate_relaxed_api_security(request: Request) -> Dict[str, Any]:
    """Minimal security validation for API endpoints with relaxed security for all users"""
    client_ip = security_manager.get_client_ip(request)
    
    # Skip IP validation entirely for maximum leniency
    # Chinese partners may use various proxy configurations
    
    # Skip rate limiting for relaxed security mode
    # Chinese partners need higher limits for testing and integration
    
    return {
        "client_ip": client_ip,
        "validated": True,
        "security_level": "relaxed_lenient",
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Security validation bypassed for Chinese partner compatibility"
    }