# Chinese Manufacturer API Documentation

**Version:** 2.1.0  
**Base URL:** `https://pimpmycase.onrender.com`  
**Testing URL:** `http://localhost:8000` (for local testing)

This document provides comprehensive API documentation for Chinese manufacturers to integrate with the PimpMyCase platform for payment status updates, equipment management, stock management, print commands, and image downloading.

## Table of Contents

1. [Overview](#overview)
2. [Recent Updates (v2.1.0)](#recent-updates-v210)
3. [Authentication & Security](#authentication--security)
4. [API Endpoints](#api-endpoints)
5. [Data Models](#data-models)
6. [Error Handling](#error-handling)
7. [Testing Guide](#testing-guide)
8. [Integration Flow](#integration-flow)

---

## Overview

The PimpMyCase API provides comprehensive endpoints for Chinese manufacturers to:

- **Receive payment status updates** from Chinese payment systems (NEW)
- **Manage equipment information** and status tracking (NEW)
- **Monitor and update stock levels** for phone models (NEW)
- **Access UK-hosted images** via secure download links (NEW)
- **Receive print commands** and send status updates
- **Track real-time order status** and queue management

### Key Features

- RESTful API design with JSON payloads
- **Enhanced security** with relaxed restrictions for Chinese partners
- **10x higher rate limits** for Chinese manufacturer endpoints
- **Automatic print command triggering** when payments are confirmed
- **UK-hosted image infrastructure** with secure token-based downloads
- Real-time payment status synchronization
- Comprehensive equipment and stock management

---

## Recent Updates (v2.1.0)

### 🚀 NEW: Payment Status Integration
- **`POST /api/chinese/order/payStatus`** - Receive payment confirmations from Chinese payment systems
- **`GET /api/chinese/payment/{third_id}/status`** - Real-time payment status checking
- **Automatic print command triggering** when payment status = 3 (paid)

### 🏭 NEW: Equipment Management
- **`GET /api/chinese/equipment/{equipment_id}/info`** - Get equipment status and recent orders
- **`POST /api/chinese/equipment/{equipment_id}/stock`** - Update stock levels for specific equipment

### 📦 NEW: Stock Management
- **`GET /api/chinese/models/stock-status`** - Get stock status for all phone models
- **Automatic stock tracking** with Chinese model IDs (CN_BRAND_XXX format)

### 🖼️ NEW: UK-Hosted Image Infrastructure
- **`GET /api/chinese/order/{order_id}/download-links`** - Get secure download links for order images
- **`GET /api/chinese/images/batch-download`** - Batch download multiple order images
- **Token-based security** for image access with HMAC signatures

### 🔧 NEW: Print Management
- **`POST /api/chinese/print/trigger`** - Trigger print jobs for specific orders
- **`GET /api/chinese/print/{order_id}/status`** - Check print status

### 🔒 Enhanced Security & Performance
- **Relaxed security restrictions** for Chinese partner IPs
- **10x higher rate limits** (300 requests/minute vs 30 for regular users)
- **Improved timezone handling** for consistent datetime operations
- **Better error handling** with detailed validation messages

---

## Authentication & Security

### Chinese Partner Benefits
Chinese manufacturers receive enhanced API access with:
- **No authentication required** for testing and initial integration
- **10x higher rate limits** (300 requests/minute)
- **Relaxed security validation** for faster processing
- **Priority support** for integration issues

**Headers Required:**
```
Content-Type: application/json
```

**Rate Limits:**
- Chinese partners: 300 requests/minute
- Regular users: 30 requests/minute

---

## API Endpoints

### 1. Test Connection

**Endpoint:** `GET /api/chinese/test-connection`  
**Purpose:** Verify API connectivity and get available endpoints

#### Response
```json
{
  "status": "success",
  "message": "Chinese manufacturer API connection successful",
  "api_version": "2.1.0",
  "timestamp": "2025-01-29T09:00:00.000Z",
  "endpoints": {
    "test_connection": "/api/chinese/test-connection",
    "pay_status": "/api/chinese/order/payStatus",
    "payment_check": "/api/chinese/payment/{third_id}/status",
    "equipment_info": "/api/chinese/equipment/{equipment_id}/info",
    "stock_status": "/api/chinese/models/stock-status",
    "stock_update": "/api/chinese/equipment/{equipment_id}/stock",
    "print_trigger": "/api/chinese/print/trigger",
    "print_status": "/api/chinese/print/{order_id}/status",
    "download_links": "/api/chinese/order/{order_id}/download-links",
    "batch_download": "/api/chinese/images/batch-download",
    "order_status_update": "/api/chinese/order-status-update",
    "send_print_command": "/api/chinese/send-print-command"
  }
}
```

---

### 2. Payment Status Update (NEW)

**Endpoint:** `POST /api/chinese/order/payStatus`  
**Purpose:** Receive payment confirmations from Chinese payment systems

#### Request Body
```json
{
  "third_id": "CHINESE_PAYMENT_ID_12345",
  "status": 3
}
```

#### Status Values
- `1` - Waiting for payment
- `2` - Payment processing  
- `3` - Payment successful (triggers automatic print command)
- `4` - Payment failed
- `5` - Payment abnormal/error

#### Response
```json
{
  "msg": "Payment status updated successfully",
  "code": 200,
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": 3
}
```

#### Example cURL
```bash
curl -X POST "https://pimpmycase.onrender.com/api/chinese/order/payStatus" \
  -H "Content-Type: application/json" \
  -d '{
    "third_id": "CHINESE_PAYMENT_ID_12345",
    "status": 3
  }'
```

---

### 3. Payment Status Check (NEW)

**Endpoint:** `GET /api/chinese/payment/{third_id}/status`  
**Purpose:** Check real-time payment status for Chinese payment IDs

#### Response
```json
{
  "success": true,
  "third_id": "CHINESE_PAYMENT_ID_12345",
  "status": 3,
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "payment_status": "paid",
  "total_amount": 21.99,
  "currency": "GBP",
  "created_at": "2025-01-29T09:00:00.000Z",
  "paid_at": "2025-01-29T09:05:00.000Z"
}
```

---

### 4. Equipment Management (NEW)

**Endpoint:** `GET /api/chinese/equipment/{equipment_id}/info`  
**Purpose:** Get equipment status and recent order information

#### Response
```json
{
  "success": true,
  "equipment_id": "VM_TEST_MANUFACTURER",
  "equipment_info": {
    "id": "VM_TEST_MANUFACTURER",
    "name": "Chinese Manufacturer Test Unit",
    "location": "API Testing Environment",
    "is_active": true,
    "status": "online"
  },
  "recent_orders": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "printing",
      "payment_status": "paid",
      "total_amount": 21.99,
      "created_at": "2025-01-29T09:00:00.000Z"
    }
  ]
}
```

---

### 5. Stock Management (NEW)

**Endpoint:** `GET /api/chinese/models/stock-status`  
**Purpose:** Get stock status for all phone models

#### Response
```json
{
  "success": true,
  "models": [
    {
      "id": "iphone-iphone-15-pro",
      "name": "iPhone 15 Pro",
      "chinese_model_id": "CN_IPHONE_001",
      "brand": "iPhone",
      "stock": 100,
      "price": 19.99,
      "is_available": true
    }
  ],
  "total_models": 58,
  "in_stock_models": 58,
  "out_of_stock_models": 0
}
```

**Endpoint:** `POST /api/chinese/equipment/{equipment_id}/stock`  
**Purpose:** Update stock levels for specific equipment

#### Request Body
```json
{
  "stock_updates": [
    {
      "model_id": "CN_IPHONE_001",
      "stock": 50
    }
  ]
}
```

---

### 6. UK-Hosted Image Downloads (NEW)

**Endpoint:** `GET /api/chinese/order/{order_id}/download-links`  
**Purpose:** Get secure download links for order images

#### Response
```json
{
  "success": true,
  "order_id": "ORDER_CHINESE_TEST_001",
  "uk_hosting": true,
  "download_links": [
    {
      "image_id": "img_001",
      "download_url": "https://pimpmycase.onrender.com/image/secure_image_123.png?token=abc123&expires=1706529600",
      "expires_at": "2025-01-29T12:00:00.000Z",
      "image_type": "generated"
    }
  ]
}
```

**Endpoint:** `GET /api/chinese/images/batch-download`  
**Purpose:** Download images for multiple orders

#### Query Parameters
- `order_ids` - Comma-separated list of order IDs

#### Response
```json
{
  "success": true,
  "batch_downloads": [
    {
      "order_id": "ORDER_CHINESE_TEST_001",
      "success": true,
      "download_links": [...],
      "image_count": 2
    }
  ],
  "successful_orders": 1,
  "failed_orders": 0
}
```

---

### 7. Print Management (NEW)

**Endpoint:** `POST /api/chinese/print/trigger`  
**Purpose:** Trigger print job for a specific order

#### Request Body
```json
{
  "order_id": "ORDER_CHINESE_TEST_001"
}
```

#### Response
```json
{
  "success": true,
  "message": "Print job triggered successfully",
  "order_id": "ORDER_CHINESE_TEST_001",
  "print_job_id": "PRINT_12345",
  "image_urls": [
    "https://pimpmycase.onrender.com/image/secure_image_123.png?token=abc123"
  ],
  "phone_model": "iPhone 15 Pro",
  "status": "triggered"
}
```

**Endpoint:** `GET /api/chinese/print/{order_id}/status`  
**Purpose:** Check print status for an order

#### Response
```json
{
  "success": true,
  "order_id": "ORDER_CHINESE_TEST_001",
  "status": "printing",
  "print_job_id": "PRINT_12345",
  "progress": "50%",
  "estimated_completion": "2025-01-29T10:30:00.000Z"
}
```

---

### 8. Order Status Update

**Endpoint:** `POST /api/chinese/order-status-update`  
**Purpose:** Send order status updates to PimpMyCase system

#### Request Body
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "printing",
  "queue_number": "Q001",
  "estimated_completion": "2025-01-29T14:30:00.000Z",
  "chinese_order_id": "CHN_ORD_12345",
  "notes": "Order is currently being processed"
}
```

#### Valid Status Values
- `"pending"` - Order pending processing
- `"printing"` - Currently being printed
- `"printed"` - Printing completed
- `"completed"` - Ready for collection/delivery
- `"failed"` - Manufacturing failed
- `"cancelled"` - Order cancelled

---

### 9. Send Print Command

**Endpoint:** `POST /api/chinese/send-print-command`  
**Purpose:** Receive print commands from PimpMyCase system

#### Request Body
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "image_urls": [
    "https://pimpmycase.onrender.com/image/secure_image_123.png?token=abc123"
  ],
  "phone_model": "iPhone 15 Pro",
  "customer_info": {
    "vending_machine_id": "VM_001",
    "session_id": "session_12345",
    "third_party_payment_id": "CHINESE_PAYMENT_ID_12345"
  },
  "priority": 1
}
```

#### Response
```json
{
  "success": true,
  "message": "Print command received successfully",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "command_id": "CMD_ORDER_1706529600",
  "status": "received",
  "image_count": 1,
  "phone_model": "iPhone 15 Pro"
}
```

---

## Data Models

### PayStatusRequest (NEW)
```typescript
interface PayStatusRequest {
  third_id: string;     // Required: Chinese payment system ID
  status: number;       // Required: Payment status (1-5)
}
```

### StockUpdateRequest (NEW)
```typescript
interface StockUpdateRequest {
  stock_updates: Array<{
    model_id: string;   // Required: Chinese model ID (e.g., "CN_IPHONE_001")
    stock: number;      // Required: New stock quantity
  }>;
}
```

### PrintTriggerRequest (NEW)
```typescript
interface PrintTriggerRequest {
  order_id: string;     // Required: Order ID to print
}
```

### OrderStatusUpdateRequest
```typescript
interface OrderStatusUpdateRequest {
  order_id: string;                    // Required: UUID of the order
  status: string;                      // Required: Order status
  queue_number?: string;               // Optional: Queue position
  estimated_completion?: string;       // Optional: ISO 8601 timestamp
  chinese_order_id?: string;          // Optional: Your internal order ID
  notes?: string;                     // Optional: Status notes
}
```

### PrintCommandRequest
```typescript
interface PrintCommandRequest {
  order_id: string;                    // Required: UUID of the order
  image_urls: string[];               // Required: Secure image URLs
  phone_model: string;                // Required: Phone model name
  customer_info: {                    // Required: Customer information
    vending_machine_id?: string;
    session_id?: string;
    third_party_payment_id?: string;
  };
  priority?: number;                  // Optional: Print priority (1-10)
}
```

---

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid data)
- `404` - Not Found (resource doesn't exist)
- `422` - Validation Error (field validation failed)
- `500` - Internal Server Error

### Error Response Format
```json
{
  "detail": "Validation error: Status must be 1-5",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-01-29T09:00:00.000Z"
}
```

### Common Error Scenarios
- **Payment ID not found**: Returns success but logs for future order linking
- **Invalid status values**: Returns 422 with validation details
- **Missing required fields**: Returns 422 with field requirements
- **Order not found**: Returns 404 with order ID

---

## Testing Guide

### Prerequisites
1. HTTP client (cURL, Postman, or similar)
2. Access to `https://pimpmycase.onrender.com` or local test server

### Step 1: Test Connection
```bash
curl -X GET "https://pimpmycase.onrender.com/api/chinese/test-connection"
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Chinese manufacturer API connection successful",
  "api_version": "2.1.0",  
  "client_ip": "your.ip.address",
  "security_level": "relaxed_chinese_partner",
  "debug_info": {
    "rate_limit": "500 requests/minute",
    "authentication": "not_required",
    "session_validation": "flexible_format_supported"
  },
  "available_machine_ids": [
    "VM_TEST_MANUFACTURER",
    "10HKNTDOH2BA", 
    "CN_DEBUG_01",
    "VM001",
    "VM002"
  ],
  "session_format": "MACHINE_ID_YYYYMMDD_HHMMSS_RANDOM",
  "session_example": "10HKNTDOH2BA_20250729_143022_A1B2C3"
}
```

---

## 🔧 Debugging Guide for Chinese Developers

### Machine IDs for Testing

Use these pre-configured machine IDs for testing:

| Machine ID | Purpose | Location | Timeout |
|------------|---------|----------|---------|
| `VM_TEST_MANUFACTURER` | Basic testing | API Testing Environment | 60 min |
| `10HKNTDOH2BA` | Debug testing | Hong Kong Debug Environment | 120 min |
| `CN_DEBUG_01` | API integration | China API Testing Environment | 180 min |
| `VM001` | Production-like testing | Mall Kiosk Simulation | 30 min |
| `VM002` | Production-like testing | Mall Kiosk Simulation | 30 min |

### Session ID Format Requirements

**Correct Format:** `MACHINE_ID_YYYYMMDD_HHMMSS_RANDOM`

**Examples:**
- ✅ `10HKNTDOH2BA_20250729_143022_A1B2C3` 
- ✅ `VM_TEST_MANUFACTURER_20250729_173422_XYZ789`
- ✅ `CN_DEBUG_01_20250730_093542_DEF456`
- ❌ `10HKNTDOH2BA_2025729_093542_A1B2C3` (incorrect date format)
- ❌ `VM001_20250123_143022_A1B2C3?qr=true` (contains query parameters)

### Debug Session ID Validation

**Endpoint:** `GET /api/chinese/debug/session-validation/{session_id}`

**Example:**
```bash
curl -X GET "https://pimpmycase.onrender.com/api/chinese/debug/session-validation/10HKNTDOH2BA_20250729_143022_A1B2C3"
```

**Response:**
```json
{
  "session_id": "10HKNTDOH2BA_20250729_143022_A1B2C3",
  "is_valid": true,
  "is_chinese_partner": true,
  "client_ip": "61.140.95.219",
  "validation_details": {
    "length": 38,
    "parts_count": 4,
    "parts": ["10HKNTDOH2BA", "20250729", "143022", "A1B2C3"],
    "expected_format": "MACHINE_ID_YYYYMMDD_HHMMSS_RANDOM",
    "example_valid": "10HKNTDOH2BA_20250729_143022_A1B2C3"
  },
  "suggestions": ["Session ID format is valid!"]
}
```

### Common Issues & Solutions

#### Issue 1: 400 Bad Request - Invalid session ID format
**Problem:** Session ID doesn't match the expected pattern
**Solution:** Use the debug endpoint to validate your session ID format

#### Issue 2: Date format errors  
**Problem:** Using `2025729` instead of `20250729`
**Solution:** Always use 8-digit date format: `YYYYMMDD`

#### Issue 3: Query parameters in session ID
**Problem:** Including `?qr=true&machine_id=...` in the session ID
**Solution:** Session ID should only contain the core identifier, not URL parameters

#### Issue 4: Case sensitivity
**Problem:** Using lowercase characters in random part
**Solution:** Chinese partners support flexible case sensitivity, both upper and lower case work

### Step 2: Test Payment Status Update
```bash
curl -X POST "https://pimpmycase.onrender.com/api/chinese/order/payStatus" \
  -H "Content-Type: application/json" \
  -d '{
    "third_id": "TEST_PAYMENT_12345",
    "status": 3
  }'
```

### Step 3: Test Equipment Status
```bash
curl -X GET "https://pimpmycase.onrender.com/api/chinese/equipment/VM_TEST_MANUFACTURER/info"
```

### Step 4: Test Stock Status
```bash
curl -X GET "https://pimpmycase.onrender.com/api/chinese/models/stock-status"
```

### Step 5: Test Image Downloads
```bash
curl -X GET "https://pimpmycase.onrender.com/api/chinese/order/ORDER_CHINESE_TEST_001/download-links"
```

---

## Integration Flow

### Complete Order Flow with Chinese Integration

```
1. Customer Order → 2. Payment → 3. Chinese Payment System → 4. payStatus API → 5. Auto Print Trigger → 6. Manufacturing → 7. Status Updates → 8. Completion
```

#### Detailed Flow:
1. **Customer places order** on PimpMyCase platform
2. **Payment processed** via Stripe or vending machine
3. **Chinese payment system** processes payment
4. **Payment confirmation** sent via `POST /api/chinese/order/payStatus`
5. **Automatic print command** triggered when status = 3 (paid)
6. **Manufacturing begins** with image downloads from UK servers
7. **Status updates** sent via `POST /api/chinese/order-status-update`
8. **Order completion** and customer notification

### Payment Status Integration
```
Chinese Payment System → payStatus API (status=3) → Auto Print Trigger → Manufacturing
```

### Image Download Flow
```
Print Command Received → Access UK Image URLs → Download with Secure Tokens → Manufacturing
```

---

## Production Notes

### Performance Optimizations
- **Chinese partners**: 10x higher rate limits (300 req/min)
- **Optimized endpoints**: Reduced latency for Chinese manufacturing
- **Batch operations**: Support for bulk image downloads
- **Secure tokens**: HMAC-signed URLs for image access

### Monitoring & Support
- **Real-time monitoring** of all Chinese partner API calls
- **Detailed logging** for integration troubleshooting
- **Performance metrics** tracking response times
- **24/7 support** for critical manufacturing issues

### Security Features
- **IP-based recognition** for Chinese partners
- **Relaxed validation** for faster processing
- **Secure image tokens** with expiration
- **Rate limit exemptions** for manufacturing systems

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2025-01-29 | **MAJOR UPDATE**: Added payment status integration, equipment management, stock management, UK-hosted images, print management, enhanced security |
| 2.0.0 | 2025-01-24 | Initial API documentation for Chinese manufacturers |

---

## Recent Bug Fixes & Improvements (v2.1.0)

### 🔧 Technical Improvements:
- **Modern FastAPI lifespan** - Updated from deprecated `@app.on_event` to `@asynccontextmanager`
- **Enhanced error handling** - Better exception management with detailed logging
- **Improved database initialization** - More reliable sample data creation for testing
- **Consistent timezone usage** - All datetime operations now use UTC with timezone awareness

---

**Ready for Production Integration**: This API is fully tested and ready for Chinese manufacturer integration. All endpoints are functional with comprehensive error handling and monitoring.

**Support Contact**: For integration support or questions, please contact the PimpMyCase development team.