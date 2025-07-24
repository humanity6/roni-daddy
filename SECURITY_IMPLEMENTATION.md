# Security Implementation for Vending Machine API

## Overview

This document outlines the comprehensive security measures implemented for the PimpMyCase vending machine and QR code integration system.

## Security Features Implemented

### 1. Input Validation and Sanitization

#### Session ID Validation
- **Format Validation**: Session IDs must follow pattern `^[A-Z0-9_]+_\d{8}_\d{6}_[A-F0-9]{8}$`
- **Length Limits**: Maximum 200 characters
- **Character Restrictions**: Only alphanumeric, underscores allowed

#### Machine ID Validation
- **Format**: Alphanumeric with underscores and hyphens only
- **Length**: Maximum 50 characters
- **Pattern**: `^[a-zA-Z0-9_-]+$`

#### Input Sanitization
- **String Inputs**: Remove control characters, HTML tags, null bytes
- **JSON Size Limits**: Order data max 100KB, payment data max 50KB, metadata max 10KB
- **Text Truncation**: Automatic truncation to prevent buffer overflows

### 2. Rate Limiting and Abuse Prevention

#### Per-IP Rate Limiting
- **Session Status**: 30 requests per minute
- **Session Creation**: 10 requests per minute
- **Failed Attempts Tracking**: 5 failed attempts = 10 minute IP block

#### Per-Session Rate Limiting
- **Session Activity**: 20 requests per minute per session
- **Automatic cleanup** of old rate limit entries

#### Per-Machine Limits
- **Concurrent Sessions**: Maximum 5 active sessions per machine
- **Creation Rate**: 10 sessions per minute per machine

### 3. Session Security

#### Session Management
- **Unique Session IDs**: Cryptographically secure random generation
- **Expiration Handling**: Automatic cleanup of expired sessions
- **State Validation**: Strict session state transitions
- **Activity Tracking**: Last activity timestamps for all operations

#### Session Data Protection
- **IP Address Tracking**: Record and validate client IPs
- **User Agent Logging**: Track browser/device information
- **Security Metadata**: Store security validation info with sessions

### 4. Payment Security

#### Amount Validation
- **Range Checking**: £1.00 - £500.00 allowed
- **Type Validation**: Must be valid float/decimal
- **Precision**: Penny-accurate comparison (±0.01)

#### Payment Method Validation
- **Allowed Methods**: card, cash, contactless, mobile only
- **Transaction ID**: Required, sanitized, max 100 characters
- **Data Size Limits**: Payment metadata max 50KB

#### Payment Flow Security
- **State Validation**: Must be in payment_pending state
- **Amount Matching**: Payment amount must match order total
- **Duplicate Prevention**: Transaction ID uniqueness checking

### 5. Machine Authentication

#### Machine Validation
- **Database Verification**: Machine must exist and be active
- **Location Validation**: Optional but sanitized if provided
- **Session Limits**: Prevent machine session exhaustion

### 6. Brute Force Protection

#### Failed Attempt Tracking
- **IP-based Blocking**: Track failed session lookups
- **Progressive Penalties**: Escalating block duration
- **Automatic Reset**: Reset counters on successful operations

#### Monitoring
- **Suspicious Activity Detection**: Multiple failed attempts
- **IP Reputation**: Track problematic IP addresses
- **Session Hijacking Prevention**: Validate IP consistency

### 7. Data Protection

#### Sensitive Data Handling
- **PII Sanitization**: Clean user agent strings, locations
- **Payment Data**: Secure storage with audit trail
- **Session Cleanup**: Automatic removal of expired sessions

#### Audit Trail
- **Security Events**: Log all security validations
- **Timestamps**: All operations timestamped
- **IP Tracking**: Complete IP address history

## API Security Endpoints

### Session Validation
```http
POST /api/vending/session/{session_id}/validate
```
- Real-time security validation
- Session health checking
- Security metrics reporting

### Security Headers
All endpoints include:
- `security_validated: true` in responses
- Client IP validation
- Request timestamp validation

## Security Configuration

### Environment Variables
```bash
# Security settings (defaults shown)
SECURITY_RATE_LIMIT_REQUESTS=30
SECURITY_RATE_LIMIT_WINDOW=60
SECURITY_MAX_FAILED_ATTEMPTS=5
SECURITY_BLOCK_DURATION=600
SECURITY_MAX_MACHINE_SESSIONS=5
```

### Rate Limit Headers
```http
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1674123456
X-Security-Validated: true
```

## Implementation Files

### Core Security Module
- **security_middleware.py**: Main security implementation
- **SecurityManager class**: Centralized security operations
- **Validation functions**: Input validation and sanitization

### API Integration
- **api_server.py**: Security validation in all vending endpoints
- **Request validation**: All endpoints use security middleware
- **Error handling**: Secure error responses

## Security Testing

### Test Scenarios Covered
1. **Invalid Session IDs**: Malformed, too long, wrong format
2. **Rate Limiting**: Exceed request limits per IP/session
3. **Payment Validation**: Invalid amounts, mismatched totals
4. **Session State**: Invalid state transitions
5. **Brute Force**: Multiple failed session lookups
6. **Input Validation**: Malicious strings, oversized data

### Example Security Test
```bash
# Test rate limiting
for i in {1..35}; do
  curl -X GET "https://pimpmycase.onrender.com/api/vending/session/TEST_001/status"
done
# Should return 429 after 30 requests
```

## Monitoring and Alerts

### Security Metrics
- **Failed attempts per IP**
- **Blocked IP addresses**
- **Rate limit violations**
- **Invalid session access attempts**
- **Payment validation failures**

### Recommended Monitoring
```python
# Check for security issues
GET /api/vending/security/metrics
{
  "blocked_ips": ["192.168.1.100"],
  "rate_limit_violations": 25,
  "failed_attempts": 150,
  "suspicious_sessions": ["VM001_20250123_143022_A1B2C3"]
}
```

## Best Practices for Chinese Manufacturers

### 1. IP Whitelisting
- Register your vending machine IPs
- Use consistent IP addresses
- Implement failover IPs if needed

### 2. Request Patterns
- Don't exceed rate limits
- Implement exponential backoff
- Cache session status when possible

### 3. Error Handling
- Respect 429 rate limit responses
- Handle 410 expired session responses
- Implement retry logic with delays

### 4. Security Headers
- Always validate `security_validated: true` in responses
- Monitor for security-related error codes
- Log security events for audit

## Security Incident Response

### Common Issues
1. **Rate Limited**: Wait for reset time, implement backoff
2. **Session Expired**: Create new session, update QR code
3. **Payment Mismatch**: Verify amounts match exactly
4. **IP Blocked**: Contact support, check for malicious activity

### Emergency Contacts
- **Security Issues**: [To be provided]
- **API Support**: [To be provided]
- **Technical Emergency**: [To be provided]

---