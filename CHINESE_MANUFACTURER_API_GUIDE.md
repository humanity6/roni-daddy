# Chinese Manufacturer API Integration Guide
## PimpMyCase System Integration Documentation

**Version:** 2.1.0  
**Last Updated:** August 2025  
**Base URL:** `https://pimpmycase.onrender.com` (Production) | `http://localhost:8000` (Development)

---

## Overview

This guide provides comprehensive documentation for integrating Chinese manufacturing equipment with the PimpMyCase system. The API enables real-time communication between vending machines, payment systems, and printing equipment.

## Authentication & Security

- **No API Key Required:** All Chinese partner endpoints use relaxed security validation
- **Rate Limiting:** 35 requests per minute per IP address
- **IP Whitelist:** Partner IPs are automatically whitelisted for higher rate limits
- **Session Format:** Flexible session ID formats supported (both standard and Chinese formats)

---

## Core Integration Endpoints

### 1. Connection Testing

#### Test API Connection
```http
GET /api/chinese/test-connection
```

**Response:**
```json
{
  "status": "success",
  "message": "Chinese manufacturer API connection successful",
  "api_version": "2.1.0",
  "timestamp": "2025-08-02T14:42:09.492554+00:00",
  "client_ip": "127.0.0.1",
  "security_level": "relaxed_chinese_partner",
  "debug_info": {
    "rate_limit": "35 requests/minute",
    "authentication": "not_required",
    "session_validation": "flexible_format_supported"
  },
  "available_machine_ids": [
    "VM_TEST_MANUFACTURER",
    "10HKNTDOH2BA",
    "CN_DEBUG_01",
    "VM001",
    "VM002"
  ]
}
```

---

## Payment Integration

### 2. Payment Status Management

#### Query Payment Status
```http
GET /api/chinese/payment/{payment_id}/status
```

**Parameters:**
- `payment_id` (string): Unique payment identifier

**Response:**
```json
{
  "payment_id": "TEST_PAYMENT_E90225F45081",
  "status": 3,
  "status_description": "paid",
  "amount": 1999,
  "currency": "GBP",
  "created_at": "2025-08-02T14:35:00Z",
  "updated_at": "2025-08-02T14:37:15Z"
}
```

**Status Codes:**
- `1`: Waiting for payment
- `2`: Payment in progress
- `3`: Payment completed
- `4`: Payment failed
- `5`: Payment abnormal/error

#### Update Payment Status
```http
POST /api/chinese/order/payStatus
```

**Request Body:**
```json
{
  "payment_id": "TEST_PAYMENT_E90225F45081",
  "status": 3,
  "notes": "Payment confirmed by Chinese system"
}
```

**Validation:**
- `status`: Must be 1, 2, 3, 4, or 5
- `payment_id`: Required, non-empty string
- `notes`: Optional, max 500 characters

---

## Equipment Management

### 3. Equipment Information

#### Get Equipment Info
```http
GET /api/chinese/equipment/{equipment_id}/info
```

**Parameters:**
- `equipment_id` (string): Equipment identifier (e.g., "CN_DEBUG_01", "PRINTER_001")

**Response:**
```json
{
  "equipment_id": "CN_DEBUG_01",
  "status": "online",
  "location": "Beijing Manufacturing Center",
  "capabilities": {
    "max_print_size": "200x300mm",
    "supported_materials": ["TPU", "Silicone", "Hard Plastic"],
    "color_printing": true,
    "estimated_print_time": "15-30 minutes"
  },
  "current_queue": 3,
  "last_maintenance": "2025-08-01T10:00:00Z"
}
```

#### Update Equipment Stock
```http
POST /api/chinese/equipment/{equipment_id}/stock
```

**Request Body:**
```json
{
  "phone_models": {
    "iphone_14_pro": 45,
    "iphone_15": 32,
    "samsung_s24": 28
  },
  "materials": {
    "clear_tpu": 150,
    "black_silicone": 89,
    "transparent_hard": 67
  },
  "updated_by": "automated_system"
}
```

---

## Phone Model & Stock Management

### 4. Stock Status

#### Get Phone Model Stock Status
```http
GET /api/chinese/models/stock-status
```

**Response:**
```json
{
  "stock_status": {
    "iphone": {
      "iphone_14": {"available": 45, "reserved": 3},
      "iphone_14_pro": {"available": 32, "reserved": 1},
      "iphone_15": {"available": 28, "reserved": 2}
    },
    "samsung": {
      "galaxy_s24": {"available": 34, "reserved": 1},
      "galaxy_s23": {"available": 19, "reserved": 0}
    }
  },
  "last_updated": "2025-08-02T14:30:00Z",
  "total_capacity": 200,
  "total_available": 158
}
```

---

## Order Processing

### 5. Order Management

#### Update Order Status
```http
POST /api/chinese/order-status-update
```

**Request Body:**
```json
{
  "order_id": "ORDER_a819e123",
  "status": "printing",
  "estimated_completion": "2025-08-02T15:30:00Z",
  "notes": "Started printing process",
  "equipment_id": "CN_DEBUG_01"
}
```

**Valid Status Values:**
- `pending`: Order received, queued for processing
- `printing`: Currently being printed
- `printed`: Printing completed
- `completed`: Order fully completed and shipped
- `failed`: Order failed (provide reason in notes)
- `cancelled`: Order cancelled

#### Send Print Command
```http
POST /api/chinese/send-print-command
```

**Request Body:**
```json
{
  "order_id": "ORDER_a819e123",
  "equipment_id": "CN_DEBUG_01",
  "priority": 1,
  "print_settings": {
    "material": "TPU",
    "color": "transparent",
    "quality": "high"
  }
}
```

**Priority Levels:**
- `1`: High priority (rush orders)
- `2`: Normal priority
- `3`: Low priority (batch orders)

---

## Print Management

### 6. Print Operations

#### Trigger Print Job
```http
POST /api/chinese/print/trigger
```

**Request Body:**
```json
{
  "order_id": "ORDER_a819e123",
  "equipment_id": "CN_DEBUG_01",
  "print_data": {
    "design_url": "https://example.com/design.png",
    "phone_model": "iphone_14_pro",
    "template": "classic",
    "text": "Custom Text",
    "font": "Arial",
    "color": "#000000"
  }
}
```

#### Check Print Status
```http
GET /api/chinese/print/{order_id}/status
```

**Response:**
```json
{
  "order_id": "ORDER_a819e123",
  "print_status": "completed",
  "progress": 100,
  "started_at": "2025-08-02T14:45:00Z",
  "completed_at": "2025-08-02T15:15:00Z",
  "equipment_id": "CN_DEBUG_01",
  "quality_check": "passed"
}
```

---

## File Management

### 7. Download & File Operations

#### Get Order Download Links
```http
GET /api/chinese/order/{order_id}/download-links
```

**Response:**
```json
{
  "order_id": "ORDER_a819e123",
  "download_links": {
    "design_file": "https://cdn.pimpmycase.com/designs/ORDER_a819e123_design.png",
    "print_file": "https://cdn.pimpmycase.com/print/ORDER_a819e123_print.gcode",
    "preview": "https://cdn.pimpmycase.com/preview/ORDER_a819e123_preview.jpg"
  },
  "expiry": "2025-08-09T14:42:00Z"
}
```

#### Batch Download Images
```http
GET /api/chinese/images/batch-download?order_ids=ORDER_1&order_ids=ORDER_2&format=zip
```

**Query Parameters:**
- `order_ids`: Array of order IDs to download
- `format`: `zip` or `tar` (default: zip)

**Response:**
- Content-Type: `application/zip` or `application/x-tar`
- Binary file download containing all requested images

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid request format or parameters |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Request data failed validation |
| 429 | Rate Limited | Too many requests, slow down |
| 500 | Server Error | Internal server error |

### Error Response Format

```json
{
  "detail": "Error description",
  "validation_errors": [
    {
      "field": "status",
      "message": "Status must be one of: ['pending', 'printing', 'printed', 'completed', 'failed', 'cancelled']",
      "received_value": "invalid_status"
    }
  ],
  "timestamp": "2025-08-02T14:42:00Z"
}
```

---

## Integration Examples

### Python Integration Example

```python
import requests
import json

class PimpMyCaseAPI:
    def __init__(self, base_url="https://pimpmycase.onrender.com"):
        self.base_url = base_url
        
    def test_connection(self):
        response = requests.get(f"{self.base_url}/api/chinese/test-connection")
        return response.json()
        
    def update_payment_status(self, payment_id, status, notes=""):
        data = {
            "payment_id": payment_id,
            "status": status,
            "notes": notes
        }
        response = requests.post(
            f"{self.base_url}/api/chinese/order/payStatus",
            json=data
        )
        return response.json()
        
    def get_stock_status(self):
        response = requests.get(f"{self.base_url}/api/chinese/models/stock-status")
        return response.json()
        
    def update_order_status(self, order_id, status, equipment_id, notes=""):
        data = {
            "order_id": order_id,
            "status": status,
            "equipment_id": equipment_id,
            "notes": notes
        }
        response = requests.post(
            f"{self.base_url}/api/chinese/order-status-update",
            json=data
        )
        return response.json()

# Usage Example
api = PimpMyCaseAPI()

# Test connection
connection_status = api.test_connection()
print(f"API Status: {connection_status['status']}")

# Update payment
payment_result = api.update_payment_status("PAY_123", 3, "Payment confirmed")

# Check stock
stock = api.get_stock_status()
print(f"Total available: {stock['total_available']}")

# Update order
order_result = api.update_order_status("ORDER_456", "printing", "CN_DEBUG_01")
```

---

## Webhook Integration (Optional)

For real-time updates, you can configure webhooks:

### Webhook Endpoint Setup
```http
POST /api/chinese/webhook/configure
```

**Request Body:**
```json
{
  "webhook_url": "https://your-system.com/webhook/pimpycase",
  "events": ["order_status_change", "payment_completed", "print_finished"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload Example
```json
{
  "event": "order_status_change",
  "order_id": "ORDER_a819e123",
  "old_status": "pending",
  "new_status": "printing",
  "timestamp": "2025-08-02T14:42:00Z",
  "equipment_id": "CN_DEBUG_01"
}
```

---

## Testing & Debugging

### Test Environment
- **Base URL:** `http://localhost:8000`
- **Test Equipment ID:** `CN_DEBUG_01`
- **Test Payment ID:** `TEST_PAYMENT_*`

### Debug Information
All responses include debug information when in development mode:
```json
{
  "debug_info": {
    "request_id": "req_123456",
    "processing_time": "0.045s",
    "equipment_status": "online",
    "queue_position": 2
  }
}
```

### Health Monitoring
Use the connection test endpoint regularly to monitor API health:
```bash
curl -X GET "https://pimpmycase.onrender.com/api/chinese/test-connection"
```

---

## Support & Contact

For technical support or integration questions:
- **API Documentation:** This guide
- **System Status:** Check `/health` endpoint
- **Rate Limits:** Monitor response headers for rate limit status

## Changelog

**v2.1.0 (August 2025)**
- Added batch download functionality
- Improved error handling and validation
- Enhanced equipment management endpoints
- Added webhook support

**v2.0.0 (July 2025)**
- Complete API redesign for Chinese manufacturer integration
- Added comprehensive order management
- Implemented real-time print status tracking