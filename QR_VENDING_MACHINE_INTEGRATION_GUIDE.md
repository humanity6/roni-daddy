# QR Code & Vending Machine Integration Guide

**Version:** 2.0.0  
**Base URL:** `https://pimpmycase.onrender.com`  
**Date:** January 2025

This comprehensive guide provides everything Chinese manufacturers need to integrate QR code functionality and vending machine payment systems with the PimpMyCase platform.

## Table of Contents

1. [Overview](#overview)
2. [QR Code Generation Requirements](#qr-code-generation-requirements)
3. [Vending Machine APIs](#vending-machine-apis)
4. [Complete Integration Flow](#complete-integration-flow)
5. [Session Management](#session-management)
6. [Payment Integration](#payment-integration)
7. [Error Handling](#error-handling)
8. [Testing Guide](#testing-guide)
9. [Security Considerations](#security-considerations)

---

## Overview

The PimpMyCase platform supports two payment flows:
1. **App Payment**: User pays via Stripe on their mobile device
2. **Vending Machine Payment**: User designs on mobile, pays at vending machine

### Key Components
- **QR Code Generation**: Creates unique session-linked QR codes
- **Session Management**: Tracks user progress and vending machine state
- **Payment Integration**: Handles both app and vending machine payments
- **Real-time Communication**: Syncs state between mobile app and vending machine

---

## QR Code Generation Requirements

### 1. QR Code URL Format
```
https://pimpmycase.shop/?qr=true&machine_id={MACHINE_ID}&session_id={SESSION_ID}&location={LOCATION}
```

### 2. Required Parameters
- **qr**: Must be `true` to indicate QR session
- **machine_id**: Unique identifier for the vending machine
- **session_id**: Unique session identifier (format below)
- **location**: Optional human-readable location

### 3. Session ID Format
```
{MACHINE_ID}_{YYYYMMDD}_{HHMMSS}_{RANDOM}
```

**Example:** `VM001_20250123_143022_A1B2C3`

### 4. Example QR Code URLs
```
https://pimpmycase.shop/?qr=true&machine_id=VM001&session_id=VM001_20250123_143022_A1B2C3&location=mall_level2

https://pimpmycase.shop/?qr=true&machine_id=VM_LONDON_01&session_id=VM_LONDON_01_20250123_155030_X9Y8Z7&location=Oxford_Street_Station
```

---

## Vending Machine APIs

### 1. Create Session (Before QR Generation)

**Endpoint:** `POST /api/vending/create-session`

**Request:**
```json
{
  "machine_id": "VM001",
  "location": "Mall Level 2",
  "session_timeout_minutes": 30,
  "metadata": {
    "mall_name": "Westfield",
    "floor": 2,
    "zone": "food_court"
  }
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "VM001_20250123_143022_A1B2C3",
  "qr_url": "https://pimpmycase.shop/?qr=true&machine_id=VM001&session_id=VM001_20250123_143022_A1B2C3&location=mall_level2",
  "expires_at": "2025-01-23T15:00:22.000Z",
  "timeout_minutes": 30,
  "machine_info": {
    "id": "VM001",
    "name": "Mall Kiosk 1",
    "location": "Westfield Mall - Level 2"
  }
}
```

### 2. Monitor Session Status

**Endpoint:** `GET /api/vending/session/{session_id}/status`

**Response:**
```json
{
  "session_id": "VM001_20250123_143022_A1B2C3",
  "status": "active",
  "user_progress": "designing",
  "expires_at": "2025-01-23T15:00:22.000Z",
  "created_at": "2025-01-23T14:30:22.000Z",
  "last_activity": "2025-01-23T14:45:30.000Z",
  "machine_id": "VM001",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "payment_amount": 19.99
}
```

**Session Statuses:**
- `active` - Session created, waiting for user
- `designing` - User is designing their case
- `payment_pending` - User reached payment, awaiting machine payment
- `payment_completed` - Payment confirmed
- `expired` - Session timed out
- `cancelled` - Session cancelled

**User Progress:**
- `started` - QR generated
- `qr_scanned` - User scanned QR code
- `brand_selected` - User selected phone brand
- `design_complete` - User finished design
- `payment_reached` - User at payment screen

### 3. Receive Order Summary

When user chooses "Pay via Machine", you'll receive order details:

**Your endpoint should handle:** `POST /your-vending-machine-api/order-summary`

**Payload from PimpMyCase:**
```json
{
  "session_id": "VM001_20250123_143022_A1B2C3",
  "order_data": {
    "brand": "iPhone",
    "model": "iPhone 15 Pro",
    "color": "Natural Titanium",
    "template": {
      "id": "retro-remix",
      "name": "Retro Remix"
    },
    "designImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "inputText": "My Custom Text",
    "selectedFont": "Arial",
    "selectedTextColor": "#ffffff"
  },
  "payment_amount": 19.99,
  "currency": "GBP"
}
```

### 4. Confirm Payment

**Endpoint:** `POST /api/vending/session/{session_id}/confirm-payment`

**Request:**
```json
{
  "session_id": "VM001_20250123_143022_A1B2C3",
  "payment_method": "card",
  "payment_amount": 19.99,
  "transaction_id": "TXN_20250123_143500_001",
  "payment_data": {
    "card_last_four": "1234",
    "approval_code": "ABCD123",
    "receipt_number": "RCP123456789"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payment confirmed successfully",
  "session_id": "VM001_20250123_143022_A1B2C3",
  "transaction_id": "TXN_20250123_143500_001",
  "status": "payment_completed",
  "next_steps": "Order will be sent for printing"
}
```

### 5. Session Cleanup

**Endpoint:** `DELETE /api/vending/session/{session_id}`

Use this to clean up expired or cancelled sessions.

---

## Complete Integration Flow

### Phase 1: Session Creation & QR Display
1. **Vending Machine creates session**
   ```bash
   curl -X POST "https://pimpmycase.onrender.com/api/vending/create-session" \
     -H "Content-Type: application/json" \
     -d '{
       "machine_id": "VM001",
       "location": "Mall Level 2",
       "session_timeout_minutes": 30
     }'
   ```

2. **Display QR code on vending machine screen**
   - Show the returned `qr_url` as QR code
   - Display session timeout countdown
   - Show instructions: "Scan QR code with your phone to start designing"

### Phase 2: User Interaction
3. **User scans QR code**
   - Mobile browser opens PimpMyCase web app
   - App detects QR parameters and registers with session
   - Vending machine receives status update: `user_progress: "qr_scanned"`

4. **Monitor user progress**
   ```bash
   # Poll this endpoint every 10-15 seconds
   curl -X GET "https://pimpmycase.onrender.com/api/vending/session/VM001_20250123_143022_A1B2C3/status"
   ```

5. **User designs case**
   - User selects brand, model, template
   - Uploads/takes photos, adds text
   - Progress updates: `brand_selected` → `design_complete` → `payment_reached`

### Phase 3: Payment Decision
6. **User reaches payment screen**
   - User sees two options: "Pay on App" or "Pay via Machine"
   - If "Pay via Machine" → Order summary sent to vending machine
   - If "Pay on App" → Normal Stripe flow, order sent for printing

### Phase 4: Vending Machine Payment
7. **Receive order summary** (if user chose vending machine payment)
   - Your machine receives order details via your API endpoint
   - Display order summary: "iPhone 15 Pro Case - £19.99"
   - Show payment options (card/cash/contactless)

8. **Process payment**
   - Handle payment via your machine's payment system
   - On successful payment, confirm with PimpMyCase API

9. **Order completion**
   - PimpMyCase automatically sends order for printing
   - Display success message: "Order confirmed! Your case is being printed."

---

## Session Management

### Session Lifecycle
```
QR Generated → QR Scanned → Designing → Payment Pending → Payment Complete
     ↓              ↓           ↓             ↓               ↓
   30min          Activity    Activity     Machine        Success
  timeout        timeout     timeout      payment        → Print
```

### Polling Recommendations
- **Session Status**: Every 10-15 seconds
- **User Progress**: Every 10-15 seconds when user is active
- **Payment Status**: Every 5 seconds when payment pending

### Timeout Handling
- **Session Timeout**: 30 minutes default (configurable)
- **Activity Timeout**: Reset timer on each user action
- **Payment Timeout**: 5 minutes once payment screen reached

---

## Payment Integration

### Payment Methods Supported
- **Card**: Chip, contactless, magnetic stripe
- **Cash**: Physical cash with change dispensing
- **Mobile**: Apple Pay, Google Pay, Samsung Pay

### Payment Confirmation Requirements
- **transaction_id**: Unique transaction identifier
- **payment_amount**: Exact amount paid (must match order)
- **payment_method**: Type of payment used
- **payment_data**: Additional payment details for receipt

### Receipt Generation
After payment confirmation, provide receipt with:
- Order number
- Machine location
- Payment method and amount
- Estimated completion time
- QR code for order tracking

---

## Error Handling

### Common Error Scenarios

#### Session Not Found (404)
```json
{
  "detail": "Session not found"
}
```
**Resolution**: Session expired or invalid session_id

#### Session Expired (410)
```json
{
  "detail": "Session has expired"
}
```
**Resolution**: Create new session and generate new QR code

#### Payment Amount Mismatch
```json
{
  "detail": "Payment amount does not match order total"
}
```
**Resolution**: Verify payment amount matches order summary

#### Machine Offline
- Display "Machine temporarily offline" message
- Provide alternative: "Please try another machine or pay on your phone"

### Error Recovery
1. **Session Timeout**: Generate new QR code
2. **Network Issues**: Retry with exponential backoff
3. **Payment Failure**: Allow retry, update session status
4. **User Abandonment**: Clean up session after timeout

---

## Testing Guide

### Prerequisites
1. Access to `https://pimpmycase.onrender.com`
2. JSON HTTP client (cURL, Postman, etc.)
3. QR code generator for testing

### Step 1: Test Session Creation
```bash
curl -X POST "https://pimpmycase.onrender.com/api/vending/create-session" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "TEST_VM_001",
    "location": "Test Location",
    "session_timeout_minutes": 30
  }'
```

### Step 2: Test QR Code Flow
1. Generate QR code with returned URL
2. Scan QR code with mobile device
3. Monitor session status for updates

### Step 3: Test Payment Confirmation
```bash
curl -X POST "https://pimpmycase.onrender.com/api/vending/session/{session_id}/confirm-payment" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "TEST_VM_001_20250123_143022_A1B2C3",
    "payment_method": "card",
    "payment_amount": 19.99,
    "transaction_id": "TEST_TXN_001"
  }'
```

### Integration Test Scenarios
1. **Happy Path**: QR → Design → Vending Payment → Success
2. **App Payment**: QR → Design → App Payment → Success  
3. **Session Timeout**: QR → Wait 30min → Timeout
4. **Payment Failure**: QR → Design → Failed Payment → Retry
5. **User Abandonment**: QR → Design → User Leaves → Cleanup

---

## Security Considerations

### Session Security
- **Session IDs**: Include random component to prevent guessing
- **Timeout**: Automatic cleanup of expired sessions
- **Validation**: Verify machine_id matches registered machines
- **Rate Limiting**: Prevent session creation abuse

### Payment Security
- **Amount Validation**: Verify payment amount matches order
- **Transaction IDs**: Must be unique per machine
- **PCI Compliance**: Handle card data according to PCI standards
- **Audit Trail**: Log all payment transactions

### QR Code Security
- **Expiration**: QR codes expire with session
- **Single Use**: Each QR code valid for one session only
- **Domain Validation**: Only accept QR codes from pimpmycase.shop
- **HTTPS Only**: All communications must use HTTPS

---

## Support & Maintenance

### Monitoring Endpoints
- **Health Check**: `GET /api/chinese/test-connection`
- **Session Stats**: Track active sessions, completion rates
- **Error Rates**: Monitor API error responses

### Maintenance Windows
- **Session Cleanup**: Automated cleanup of expired sessions
- **Database Maintenance**: Regular cleanup of old session data
- **API Updates**: Backward compatibility guaranteed for 6 months

### Contact Information
- **Technical Support**: [Contact details to be provided]
- **API Documentation**: This guide + Chinese Manufacturer API docs
- **Emergency Contact**: [Emergency contact to be provided]

---

## Appendix: Example Implementation

### Vending Machine Controller Pseudocode
```python
class VendingMachineController:
    def __init__(self, machine_id, api_base_url):
        self.machine_id = machine_id
        self.api_base_url = api_base_url
        self.current_session = None
    
    def generate_qr_session(self):
        # Create session
        response = requests.post(f"{self.api_base_url}/api/vending/create-session", 
                               json={"machine_id": self.machine_id})
        session_data = response.json()
        
        # Display QR code
        qr_code = generate_qr_code(session_data["qr_url"])
        self.display_qr_code(qr_code)
        
        # Start monitoring
        self.current_session = session_data["session_id"]
        self.start_session_monitoring()
    
    def monitor_session(self):
        while self.current_session:
            status = self.get_session_status()
            
            if status["user_progress"] == "payment_pending":
                self.handle_payment_request(status)
            elif status["status"] == "expired":
                self.cleanup_session()
                break
            
            time.sleep(10)  # Poll every 10 seconds
    
    def handle_payment_request(self, session_status):
        # Display order summary
        amount = session_status["payment_amount"]
        self.display_payment_screen(f"Pay £{amount}")
        
        # Process payment
        payment_result = self.process_payment(amount)
        
        if payment_result.success:
            self.confirm_payment(payment_result)
            self.display_success_message()
        else:
            self.display_payment_error()
```

---