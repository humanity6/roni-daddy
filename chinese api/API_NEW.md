# API Documentation (Comprehensive)

This document provides a complete reference for all API endpoints, methods, parameters, responses, error codes, authentication, and signature requirements. It also includes practical notes for developers and testers.

---

## Global Requirements

- **Base URL (Test Environment):**
  - `http://app-dev.deligp.com:8500/mobileShell/en`
- **Request Method:**
  - All endpoints use `POST` unless otherwise specified.
- **Headers (Required for all requests):**
  | Header        | Value/Example                                      | Description                                 |
  |--------------|----------------------------------------------------|---------------------------------------------|
  | Content-Type | application/json (or multipart/form-data for upload)| Request content type                        |
  | req_source   | en                                                 | Request source (use `en` for UK/English)    |
  | sign         | <signature>                                        | MD5 signature (see below)                   |
  | Authorization| <token> (if required)                              | User token (from login, for protected APIs) |

### Signature Generation
- **Rule:**
  1. Sort all payload fields alphabetically by key.
  2. Concatenate all values (as strings, skip nulls).
  3. Append system name (`mobileShell`) and fixed key (`shfoa3sfwoehnf3290rqefiz4efd`).
  4. MD5 hash the resulting string.
- **Example:**
  - Payload: `{ "account": "user", "password": "pass" }`
  - Sorted: `account`, `password`
  - Value string: `userpassmobileShellshfoa3sfwoehnf3290rqefiz4efd`
  - Signature: `MD5(value_string)`
- **Header:** `sign: <md5-hash>`

### Authentication
- Obtain token via `user/login`.
- Pass token in `Authorization` header for protected endpoints.
- Token is valid for 1440 minutes.

---

## Error Codes

| Code | Meaning                                 |
|------|-----------------------------------------|
| 200  | Operation successful                    |
| 400  | Number list error (missing/format error)|
| 401  | Unauthorized, token expired             |
| 403  | Access restricted, authorization expired|
| 404  | Resource/service not found              |
| 405  | Disallowed HTTP methods                 |
| 415  | Unsupported data/menu permissions       |
| 500  | Internal system error                   |

---

## Status Codes

### Payment Status (`status` in payment APIs)
| Code | Meaning           |
|------|-------------------|
| 1    | Waiting for payment|
| 2    | Paying            |
| 3    | Paid              |
| 4    | Payment failed    |
| 5    | Payment abnormal  |

### Order Status (`status` in order APIs)
| Code | Meaning              |
|------|----------------------|
| 1    | Waiting for payment  |
| 2    | Cancelled            |
| 3    | Paying               |
| 4    | Paid                 |
| 5    | Payment failed       |
| 6    | Refunding            |
| 7    | Refunded             |
| 8    | Waiting for printing |
| 9    | Picking up           |
| 10   | Pickup completed     |
| 11   | Printing             |
| 12   | Printed              |
| 13   | Printing failed      |
| 14   | Printing canceled    |
| 15   | Shipping             |
| 16   | Shipping completed   |

---

## Endpoints

### 1. `user/login`
- **Method:** POST
- **URL:** `user/login`
- **Headers:** `Content-Type`, `req_source`, `sign`
- **Parameters:**
  | Name     | Required | Type   | Description |
  |----------|----------|--------|-------------|
  | account  | yes      | string | User account|
  | password | yes      | string | Password    |
- **Sample Request:**
```json
{
  "account": "taharizvi.ai@gmail.com",
  "password": "EN112233"
}
```
- **Sample Response:**
```json
{
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "MEA020250118000001",
    "account": "taharizvi.ai@gmail.com",
    "token": "<token-string>"
  }
}
```
- **Notes:** Save the `token` for use in subsequent requests.

---

### 2. `brand/list`
- **Method:** POST
- **URL:** `brand/list`
- **Headers:** `Content-Type`, `req_source`, `sign`, `Authorization`
- **Parameters:** _None_
- **Sample Request:**
```json
{}
```
- **Sample Response:**
```json
{
  "msg": "操作成功",
  "code": 200,
  "data": [
    { "name": "三星", "e_name": "SAMSUNG", "id": "BR020250120000001" }
  ]
}
```

---

### 3. `stock/list`
- **Method:** POST
- **URL:** `stock/list`
- **Headers:** `Content-Type`, `req_source`, `sign`, `Authorization`
- **Parameters:**
  | Name      | Required | Type   | Description |
  |-----------|----------|--------|-------------|
  | device_id | yes      | string | Device ID   |
  | brand_id  | yes      | string | Brand ID    |
- **Sample Request:**
```json
{
  "device_id": "TEST_DEVICE_001",
  "brand_id": "BR020250120000001"
}
```
- **Sample Response:**
```json
{
  "msg": "操作成功",
  "code": 200,
  "data": [
    {
      "mobile_model_name": "SAMSUNG Galaxy S22+",
      "mobile_model_id": "MM020250120000002",
      "price": 10,
      "stock": 10
    }
  ]
}
```

---

### 4. `order/payData` (Report payment information)
- **Method:** POST
- **URL:** `order/payData`
- **Headers:** `Content-Type`, `req_source`, `sign`, `Authorization`
- **Parameters:**
  | Name           | Required | Type   | Description                                      |
  |----------------|----------|--------|--------------------------------------------------|
  | mobile_model_id| yes      | string | Model ID                                         |
  | device_id      | yes      | string | Device ID                                        |
  | third_id       | yes      | string | Third-party payment ID (PYEN+yyMMdd+6 digits)    |
  | pay_amount     | yes      | double | Payment amount                                   |
  | pay_type       | yes      | int    | Payment method (see below)                       |
- **Payment Method Mapping:**
  | Code | Method         |
  |------|---------------|
  | 0    | Other         |
  | 1    | WeChat        |
  | 2    | Alipay        |
  | 3    | Unlimited Pay |
  | 4    | Cash          |
  | 5    | NAYAX         |
  | 6    | Card          |
  | 7    | On-site pay   |
- **Sample Request:**
```json
{
  "mobile_model_id": "MM20250108000001",
  "device_id": "TEST_DEVICE_001",
  "third_id": "PYEN250604000001",
  "pay_amount": 1,
  "pay_type": 1
}
```
- **Sample Response:**
```json
{
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "",
    "third_id": "PYEN250604000001"
  }
}
```

---

### 5. `order/getPayStatus` (Get payment status)
- **Method:** POST
- **URL:** `order/getPayStatus`
- **Headers:** `Content-Type`, `req_source`, `sign`, `Authorization`
- **Parameters:**
  | Name     | Required | Type | Description                 |
  |----------|----------|------|-----------------------------|
  | third_id | yes      | list | List of third-party pay IDs |
- **Sample Request:**
```json
[
  "PYEN250604000001",
  "PYEN250604000002"
]
```
- **Sample Response:**
```json
{
  "msg": "操作成功",
  "code": 200,
  "data": [
    { "third_id": "PYEN250604000001", "status": 3 }
  ]
}
```

---

### 6. `order/orderData` (Report Order information)
- **Method:** POST
- **URL:** `order/orderData`
- **Headers:** `Content-Type`, `req_source`, `sign`, `Authorization`
- **Parameters:**
  | Name           | Required | Type   | Description                                      |
  |----------------|----------|--------|--------------------------------------------------|
  | third_pay_id   | yes      | string | Third-party payment ID                           |
  | third_id       | yes      | string | Third-party order ID (OREN+yyMMdd+6 digits)      |
  | mobile_model_id| yes      | string | Model ID                                         |
  | pic            | yes      | string | Print image url                                  |
  | device_id      | yes      | string | Device ID                                        |
- **Sample Request:**
```json
{
  "third_pay_id": "PYEN250604000001",
  "third_id": "OREN250604000001",
  "mobile_model_id": "MM20250108000001",
  "pic": "https://example.com/image.png",
  "device_id": "TEST_DEVICE_001"
}
```
- **Sample Response:**
```json
{
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "",
    "third_id": "OREN250604000001",
    "queue_no": "Q001",
    "status": 8
  }
}
```

---

### 7. `order/printList` (Get printing list)
- **Method:** POST
- **URL:** `order/printList`
- **Headers:** `Content-Type`, `req_source`, `sign`, `Authorization`
- **Parameters:**
  | Name      | Required | Type   | Description |
  |-----------|----------|--------|-------------|
  | device_id | yes      | string | Device ID   |
- **Sample Request:**
```json
{
  "device_id": "TEST_DEVICE_001"
}
```
- **Sample Response:**
```json
{
  "msg": "操作成功",
  "code": 200,
  "data": [
    {
      "mobile_model_name": "SAMSUNG Galaxy S22+",
      "id": "ORDER123",
      "third_id": "OREN250604000001",
      "pic": "https://example.com/image.png",
      "queue_no": "Q001",
      "status": 8
    }
  ]
}
```

---

### 8. `file/upload` (Upload files)
- **Method:** POST
- **URL:** `file/upload`
- **Headers:** `req_source`, `sign`, `Authorization` (no Content-Type, handled by requests library)
- **Parameters:**
  | Name | Required | Type | Description                |
  |------|----------|------|----------------------------|
  | file | yes      | file | Document (multipart/form-data) |
  | type | yes      | int  | Photo type: 23 British pictures |
- **Sample Request:**
  - Use `multipart/form-data` with file and type fields.
- **Sample Response:**
```json
{
  "msg": "操作成功",
  "code": 200,
  "data": "https://weburl.ndxvs.com/mobileShell/18/20250605/a0bnab9zjrku.png"
}
```
- **Notes:**
  - Signature is generated using only the `type` field.
  - Use `files` and `data` in your HTTP client (see `full_api_test.py`).

---

## Notifications & Status Endpoints

- **Payment/Order Notification:**
  - See original API.md for real-time notification endpoints and their parameters.
  - These follow similar parameter/response patterns as above.

---

## Developer & Testing Notes

- **Test Account:**
  - `account`: `taharizvi.ai@gmail.com`
  - `password`: `EN112233`
- **Test Device ID:**
  - `TEST_DEVICE_001`
- **Signature Example (Python):**
  - See `full_api_test.py` for a working implementation.
- **File Upload:**
  - Use `multipart/form-data`.
  - Signature is based on form fields, not file content.
- **Logging & Debugging:**
  - Log all requests, headers, and responses for troubleshooting.
- **Token Expiry:**
  - If you receive a 401 error, re-login to obtain a new token.

---

**For full details and advanced flows, see the original API.md.** 