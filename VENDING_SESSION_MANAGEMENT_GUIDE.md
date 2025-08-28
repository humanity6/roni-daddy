# Vending Machine Session Management Guide

This guide explains how to manage vending machine sessions, particularly resolving "session limit exceeded" errors.

## Overview

The vending machine system has a built-in session limit of **5 concurrent active sessions per machine** to prevent resource exhaustion. When this limit is reached, new session creation will fail with the error "Machine session limit exceeded".

## Session Lifecycle

1. **Active** - Session is created and user can interact with it
2. **Designing** - User is customizing their phone case
3. **Payment Pending** - User has submitted order, waiting for payment
4. **Payment Completed** - Payment successful, order in progress
5. **Expired** - Session exceeded its time limit (default 30 minutes)
6. **Cancelled** - Session manually cancelled

## Problem: Session Limit Exceeded

### Symptoms
- Error message: "Machine session limit exceeded"
- Unable to create new QR codes/sessions for a specific machine
- Usually occurs during testing with frequent session creation

### Root Causes
1. **Expired sessions not cleaned up** - Old sessions remain in "active" status
2. **In-memory counter drift** - Security manager's session count becomes inconsistent
3. **Testing artifacts** - Multiple test sessions left active

## Solution Methods

### Method 1: Interactive Python Script (Recommended)

Use the provided interactive script for comprehensive session management:

```bash
python cleanup_cxylogd8oquk_sessions.py
```

#### Features:
- **List sessions** - View all sessions for machine CXYLOGD8OQUK
- **Smart cleanup** - Remove only expired/inactive sessions
- **Force cleanup** - Delete ALL sessions (emergency use)
- **Machine info** - Check if machine exists in database
- **Reset counter** - Fix in-memory session count

#### Example Usage:
```
Options:
1. List all sessions
2. Clean up expired/inactive sessions  ← Start here
3. Force delete ALL sessions (DANGER!)
4. Check machine information
5. Reset in-memory session count
6. Exit

Select option (1-6): 2
```

### Method 2: API Endpoints (Programmatic)

New admin API endpoints are available for session management:

#### List Sessions
```bash
GET /api/admin/machines/CXYLOGD8OQUK/sessions
```

Optional parameters:
- `status` - Filter by status (active, expired, etc.)
- `limit` - Number of sessions to return (default: 50)

#### Cleanup Sessions
```bash
DELETE /api/admin/machines/CXYLOGD8OQUK/sessions/cleanup
```

Optional parameters:
- `force=true` - Delete ALL sessions (use with caution)

#### Delete Single Session
```bash
DELETE /api/admin/sessions/{session_id}
```

#### Get Machine Info
```bash
GET /api/admin/machines/CXYLOGD8OQUK/info
```

#### Reset Session Count
```bash
POST /api/admin/machines/CXYLOGD8OQUK/reset-session-count
```

### Method 3: Direct Database Access

For emergency situations, you can directly query the database:

```sql
-- List all sessions for CXYLOGD8OQUK
SELECT session_id, status, created_at, expires_at, user_progress 
FROM vending_machine_sessions 
WHERE machine_id = 'CXYLOGD8OQUK' 
ORDER BY created_at DESC;

-- Delete expired sessions
DELETE FROM vending_machine_sessions 
WHERE machine_id = 'CXYLOGD8OQUK' 
AND (expires_at < NOW() OR status IN ('expired', 'cancelled', 'payment_completed'));

-- Delete ALL sessions (emergency)
DELETE FROM vending_machine_sessions 
WHERE machine_id = 'CXYLOGD8OQUK';
```

## Session Management Architecture

### Database Models

**VendingMachineSession** table stores:
- `session_id` - Unique session identifier
- `machine_id` - Vending machine ID
- `status` - Current session status
- `expires_at` - Session expiration time
- `user_progress` - User's progress through the flow
- `session_data` - Order details and user selections

### Security Manager

The `SecurityManager` class maintains in-memory counters:
- `machine_sessions[machine_id]` - Count of active sessions per machine
- Automatic cleanup of expired sessions
- Session limit validation (default: 5 concurrent sessions)

### Session Cleanup Process

1. **Automatic Cleanup** - Happens during session creation
   - Marks expired sessions as "expired"
   - Updates in-memory counters
   - Runs periodically (every 50th request)

2. **Manual Cleanup** - Use scripts or API endpoints
   - Identifies expired/inactive sessions
   - Deletes from database
   - Resets in-memory counters

## Best Practices

### For Development/Testing
1. **Clean up after testing** - Always clean up test sessions
2. **Use shorter timeouts** - Set session_timeout_minutes to 5-10 for testing
3. **Monitor session count** - Check active sessions before creating new ones

### For Production
1. **Monitor session health** - Set up alerts for high session counts
2. **Automatic cleanup** - Implement scheduled cleanup of old sessions
3. **Session timeout** - Use appropriate timeouts (30-60 minutes)
4. **Rate limiting** - Limit session creation frequency per IP/machine

### Recovery Procedures

#### Quick Fix (Most Common)
```bash
# Run the interactive script and choose option 2
python cleanup_cxylogd8oquk_sessions.py
```

#### Emergency Reset
```bash
# Delete ALL sessions for the machine
python cleanup_cxylogd8oquk_sessions.py
# Choose option 3 and type "DELETE ALL"
```

#### API-based Fix
```bash
# Using curl or similar tool
curl -X DELETE "https://your-api.com/api/admin/machines/CXYLOGD8OQUK/sessions/cleanup"
```

## Troubleshooting

### Session Count Mismatch
- **Problem**: In-memory count doesn't match database
- **Solution**: Use "Reset in-memory session count" option

### Machine Not Found
- **Problem**: Machine CXYLOGD8OQUK doesn't exist in database
- **Solution**: Machine will be auto-created on first session request

### Persistent Session Limit Issues
- **Check**: Network connectivity to database
- **Check**: Database permissions
- **Check**: FastAPI server restart may be needed

## Monitoring and Alerts

Consider implementing these monitoring checks:

```python
# Check for machines approaching session limit
def check_session_limits():
    for machine_id, count in security_manager.machine_sessions.items():
        if count >= 4:  # Alert at 80% of limit
            send_alert(f"Machine {machine_id} has {count}/5 active sessions")
```

## Files Reference

- `cleanup_cxylogd8oquk_sessions.py` - Interactive session management script
- `backend/routes/vending.py` - Main vending machine API endpoints  
- `backend/routes/admin.py` - Admin API endpoints for session management
- `security_middleware.py` - Session limit validation and cleanup
- `models.py` - Database models for sessions and machines

## Support

For additional issues:
1. Check server logs for detailed error messages
2. Verify database connectivity
3. Restart the FastAPI server if needed
4. Contact development team with session IDs and error details