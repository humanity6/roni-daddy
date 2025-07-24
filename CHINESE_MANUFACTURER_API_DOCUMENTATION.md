# Chinese Manufacturer API Documentation

**Version:** 2.0.0  
**Base URL:** `https://pimpmycase.onrender.com`  
**Testing URL:** `https://pimpmycase.onrender.com`  

This document provides comprehensive API documentation for Chinese manufacturers to integrate with the PimpMyCase platform for order status updates and print command communication.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Testing Guide](#testing-guide)
7. [Integration Flow](#integration-flow)

---

## Overview

The PimpMyCase API provides endpoints for Chinese manufacturers to:

- **Receive order status updates** from their manufacturing systems
- **Send print commands** to manufacturing systems  
- **Test connectivity** and verify API integration

### Key Features

- RESTful API design with JSON payloads
- Comprehensive error handling with detailed messages
- Real-time order status tracking
- Support for queue management and estimated completion times

---

## Authentication

Currently, the API does not require authentication for testing purposes. In production, authentication will be implemented using API keys or JWT tokens.

**Headers Required:**
```
Content-Type: application/json
```

---

## API Endpoints

### 1. Test Connection

**Endpoint:** `GET /api/chinese/test-connection`  
**Purpose:** Verify API connectivity and get basic system information

#### Request
```http
GET /api/chinese/test-connection
Content-Type: application/json
```

#### Response
```json
{
  "status": "success",
  "message": "Connection successful",
  "api_version": "2.0.0",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "endpoints": {
    "status_update": "/api/chinese/order-status-update",
    "test_connection": "/api/chinese/test-connection"
  }
}
```

#### Example cURL
```bash
curl -X GET "https://pimpmycase.onrender.com/api/chinese/test-connection" \
  -H "Content-Type: application/json"
```

---

### 2. Order Status Update

**Endpoint:** `POST /api/chinese/order-status-update`  
**Purpose:** Receive order status updates from Chinese manufacturing systems

#### Request Body
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "printing",
  "queue_number": "Q001",
  "estimated_completion": "2024-01-15T14:30:00.000Z",
  "chinese_order_id": "CHN_ORD_12345",
  "notes": "Order is currently being processed"
}
```

#### Response
```json
{
  "success": true,
  "message": "Order status updated successfully",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "printing",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

#### Status Values
- `"received"` - Order received by manufacturer
- `"queued"` - Order added to manufacturing queue
- `"printing"` - Currently being printed
- `"quality_check"` - In quality control
- `"packaging"` - Being packaged
- `"completed"` - Ready for collection/delivery
- `"failed"` - Manufacturing failed
- `"cancelled"` - Order cancelled

#### Example cURL
```bash
curl -X POST "https://pimpmycase.onrender.com/api/chinese/order-status-update" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "printing",
    "queue_number": "Q001",
    "estimated_completion": "2024-01-15T14:30:00.000Z",
    "chinese_order_id": "CHN_ORD_12345",
    "notes": "Order is currently being processed"
  }'
```

---

### 3. Send Print Command

**Endpoint:** `POST /api/chinese/send-print-command`  
**Purpose:** Send print commands to Chinese manufacturing systems (placeholder for future implementation)

#### Request Body
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "image_urls": [
    "https://pimpmycase.onrender.com/image/generated_image_123.png"
  ],
  "phone_model": "iPhone 15 Pro",
  "customer_info": {
    "vending_machine_id": "VM_001",
    "session_id": "session_12345"
  },
  "priority": 1
}
```

#### Response
```json
{
  "success": true,
  "message": "Print command sent successfully",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "command_id": "CMD_1705312200",
  "status": "sent",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### Example cURL
```bash
curl -X POST "https://pimpmycase.onrender.com/api/chinese/send-print-command" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "image_urls": ["https://pimpmycase.onrender.com/image/generated_image_123.png"],
    "phone_model": "iPhone 15 Pro",
    "customer_info": {
      "vending_machine_id": "VM_001",
      "session_id": "session_12345"
    },
    "priority": 1
  }'
```

---

## Data Models

### OrderStatusUpdate Request
```typescript
interface OrderStatusUpdateRequest {
  order_id: string;                    // Required: UUID of the order
  status: string;                      // Required: Current order status
  queue_number?: string;               // Optional: Queue position identifier
  estimated_completion?: string;       // Optional: ISO 8601 timestamp
  chinese_order_id?: string;          // Optional: Manufacturer's internal order ID
  notes?: string;                     // Optional: Additional status information
}
```

### PrintCommand Request
```typescript
interface PrintCommandRequest {
  order_id: string;                    // Required: UUID of the order
  image_urls: string[];               // Required: Array of image URLs to print
  phone_model: string;                // Required: Phone model for the case
  customer_info: object;              // Required: Customer/session information
  priority?: number;                  // Optional: Print priority (1-10, default: 1)
}
```

---

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid data)
- `404` - Not Found (order doesn't exist)
- `500` - Internal Server Error

### Error Response Format
```json
{
  "detail": "Order not found",
  "error_code": "ORDER_NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Common Error Codes
- `ORDER_NOT_FOUND` - The specified order ID doesn't exist
- `INVALID_STATUS` - The provided status value is not valid
- `MISSING_REQUIRED_FIELD` - A required field is missing from the request
- `INVALID_ORDER_ID` - The order ID format is invalid

---

## Testing Guide

### Prerequisites
1. Ensure your system can make HTTP requests to `https://pimpmycase.onrender.com`
2. Have a JSON HTTP client (cURL, Postman, etc.)

### Step 1: Test Connectivity
```bash
curl -X GET "https://pimpmycase.onrender.com/api/chinese/test-connection"
```

**Expected Response:** HTTP 200 with connection confirmation

### Step 2: Test Order Status Update
```bash
curl -X POST "https://pimpmycase.onrender.com/api/chinese/order-status-update" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "test-order-123",
    "status": "received",
    "queue_number": "Q001"
  }'
```

**Expected Response:** HTTP 404 (order doesn't exist) or HTTP 200 (if test order exists)

### Step 3: Test Print Command
```bash
curl -X POST "https://pimpmycase.onrender.com/api/chinese/send-print-command" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "test-order-123",
    "image_urls": ["https://example.com/test-image.png"],
    "phone_model": "iPhone 15 Pro",
    "customer_info": {"test": true},
    "priority": 1
  }'
```

**Expected Response:** HTTP 404 (order doesn't exist) or HTTP 200 (if test order exists)

---

## Integration Flow

### Typical Order Flow
1. **Customer places order** on PimpMyCase platform
2. **Order created** in PimpMyCase database with status "created"
3. **Payment processed** via Stripe or vending machine
4. **Print command sent** to Chinese manufacturer via `/api/chinese/send-print-command`
5. **Status updates received** from manufacturer via `/api/chinese/order-status-update`
6. **Customer receives updates** through the platform

### Status Update Flow
```
created → received → queued → printing → quality_check → packaging → completed
                                    ↓
                               failed (if issues occur)
```

---

## Production Notes

### Rate Limiting
- Current: No rate limiting implemented
- Production: Will implement rate limiting (TBD)

### Monitoring
- All API calls are logged
- Response times are monitored
- Error rates are tracked


---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-07-24 | Initial API documentation for Chinese manufacturers |

---

**Note:** This API is currently in testing phase. All endpoints are functional and available for integration testing. Please report any issues or questions during your testing process.