# Chinese API Documentation

## 1. Interface Configuration

**Production Environment:** `https://api.inkele.net/mobileShell/en`

**System Configuration:**

* System Name: `mobileShell`
* Fixed Key: `shfoa3sfwoehnf3290rqefiz4efd`
* Request Source: `en`

## 2. Global Error Codes

| Code | Description                                |
| ---- | ------------------------------------------ |
| 200  | Operation successful                       |
| 400  | Parameter error (missing, format mismatch) |
| 401  | Unauthorized, token expired                |
| 403  | Access restricted, authorization expired   |
| 404  | Resource/service not found                 |
| 500  | Internal system error                      |

## 3. Data Signature

**Signature Rule:** MD5(sorted parameters + system name + fixed key)

1. Sort all fields alphabetically by key
2. Concatenate only primitive values (skip objects/arrays)
3. Append system name: `mobileShell`
4. Append fixed key: `shfoa3sfwoehnf3290rqefiz4efd`
5. Generate MD5 hash (32-character lowercase string)

**Example:**

```json
{
  "user_id": "USER020250118000001",
  "page": 1,
  "rows": 10
}
```

Signature string: `110USER020250118000001mobileShellshfoa3sfwoehnf3290rqefiz4efd`
MD5 result: `85d4dabc0b38e27c382d90641eff73fd`

**Headers:**

* `sign`: The MD5 signature
* `req_source`: `en`
* `Authorization`: Token (for authenticated endpoints)
* `Content-Type`: `application/json`

## 4. Authentication

**Token Validity:** 1440 minutes (24 hours)

### Login

**Endpoint:** `user/login`
**Method:** POST

**Request:**

```json
{
  "account": "your_account",
  "password": "your_password"
}
```

**Response:**

```json
{
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "MEA020250118000001",
    "account": "your_account",
    "token": "eyJhbGciOiJIUzUxMiJ9..."
  }
}
```

## 5. Core API Endpoints

### Get Brand List

**Endpoint:** `brand/list`
**Method:** POST
**Auth:** Required

**Request:** `{}`

**Response:**

```json
{
  "msg": "操作成功",
  "code": 200,
  "data": [
    {
      "name": "苹果",
      "e_name": "Apple",
      "id": "BR20250111000002"
    }
  ]
}
```

### Get Stock List

**Endpoint:** `stock/list`
**Method:** POST
**Auth:** Required

**Request Parameters:**

| Parameter name | Required | Type   | Description |
| -------------- | -------- | ------ | ----------- |
| device\_id     | yes      | string | Device ID   |
| brand\_id      | yes      | string | Brand ID    |

**Request Example:**

```json
{
  "device_id": "CXYLOGD8OQUK",
  "brand_id": "BR20250111000002"
}
```

**Response:**

```json
{
  "msg": "操作成功",
  "code": 200,
  "data": [
    {
      "mobile_model_name": "iPhone 15 Pro",
      "mobile_model_id": "MM020250224000010",
      "mobile_shell_id": "MS102503270003",
      "width": "73.24",
      "height": "149.27",
      "stock": 2
    }
  ]
}
```

### Get Shop List

**Endpoint:** `shop/list`
**Method:** POST
**Auth:** Required

**Request:**

```json
{
  "page": 1,
  "rows": 50
}
```

**Response:**

```json
{
  "msg": "操作成功",
  "code": 200,
  "data": {
    "total": 1,
    "list": [
      {
        "name": "Roni商店",
        "id": "SP102507070001"
      }
    ]
  }
}
```

### Get Goods List

**Endpoint:** `goods/list`
**Method:** POST
**Auth:** Required

**Request:**

```json
{
  "shop_id": "SP102507070001"
}
```

**Response:**

```json
{
  "msg": "操作成功",
  "code": 200,
  "data": [
    {
      "shell_classify_id": "MS102503180003",
      "shop_id": "SP102507070001",
      "mobile_shell_id": "MS102503280009",
      "mobile_model_name": "iPhone 13",
      "brand_ename": "Apple",
      "mobile_shell_name": "iPhone 13 基础版",
      "mobile_shell_sku": "ZIP251",
      "id": "G102508260174",
      "mobile_model_id": "MM020250120000001",
      "brand_id": "BR20250111000002"
    }
  ]
}
```

### Report Payment Data

**Endpoint:** `order/payData`
**Method:** POST
**Auth:** Required

**Request:**

```json
{
  "mobile_model_id": "MM020250224000010",
  "device_id": "CXYLOGD8OQUK",
  "third_id": "PYEN250828330246",
  "pay_amount": 10.0,
  "pay_type": 1
}
```

**Response:**

```json
{
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "MSPY10250828000001",
    "third_id": "PYEN250828330246"
  }
}
```

### Report Payment Status (Chinese API calls our endpoint)

**Endpoint:** `order/payStatus`
**Method:** POST
**Auth:** Not required (webhook from Chinese system)

**Request Parameters:**

| Parameter name | Required | Type   | Description |
| -------------- | -------- | ------ | ----------- |
| third\_id      | yes      | string | Third-party payment ID |
| status         | yes      | int    | Payment status: 1=pending, 2=processing, 3=paid, 4=failed, 5=abnormal |

**Request Example:**

```json
{
  "third_id": "PYEN250830532387",
  "status": 3
}
```

**Response:**

```json
{
  "msg": "操作成功", 
  "code": 200
}
```

**Note:** The Chinese system calls OUR webhook endpoint at `/api/chinese/order/payStatus` to notify us when payment status changes. This triggers our automatic orderData call.

### Report Order Information

**Endpoint:** `order/orderData`
**Method:** POST
**Auth:** Required

**Request Parameters:**

| Parameter name    | Required | Type   | Description                                                                             |
| ----------------- | -------- | ------ | --------------------------------------------------------------------------------------- |
| third\_pay\_id    | yes      | string | Third-party payment ID                                                                  |
| third\_id         | yes      | string | Third-party order ID (rule: must be unique OREN+yyMMdd+6 digits, e.g. OREN250604000001) |
| mobile\_model\_id | yes      | string | Model ID                                                                                |
| mobile\_shell\_id | yes      | string | Phone case ID                                                                           |
| pic               | yes      | string | Print image URL                                                                         |
| device\_id        | yes      | string | Device ID                                                                               |

**Request Example:**

```json
{
  "third_pay_id": "test_pay_123",
  "third_id": "OREN250828330246",
  "mobile_model_id": "MM020250224000010",
  "mobile_shell_id": "MS102503270003",
  "pic": "https://example.com/test-image.jpg",
  "device_id": "CXYLOGD8OQUK"
}
```

**Response:**

```json
{
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "ORDER123456789",
    "third_id": "OREN250828330246",
    "queue_no": "001",
    "status": 8
  }
}
```

**Order Status Codes:**

* 1: Waiting for payment
* 2: Cancelled
* 3: Paying
* 4: Paid
* 5: Payment failed
* 6: Refunding
* 7: Refund
* 8: Waiting for printing
* 9: Picking up
* 10: Pickup completed
* 11: Printing
* 12: Printed
* 13: Printing failed
* 14: Printing canceled
* 15: Shipping
* 16: Shipping completed

## 6. Usage Examples

### Python Client Usage

```python
from chinese_api import ChineseAPIClient, ChineseAPIConfig

# Initialize client
config = ChineseAPIConfig()
client = ChineseAPIClient(
    config=config,
    account="your_account",
    password="your_password"
)

# Login
login_result = client.login()

# Get brands
brands = client.brand_list()

# Get stock for specific brand and device
stock = client.stock_list(device_id="CXYLOGD8OQUK", brand_id="BR20250111000002")

# Get shops
shops = client.shop_list()

# Get goods/products for a specific shop
goods = client.goods_list(shop_id="SP102507070001")

# Make payment
payment = client.pay_data(
    mobile_model_id="MM020250224000010",
    device_id="CXYLOGD8OQUK",
    pay_amount=10.0,
    pay_type=1
)

# Report order information
order = client.order_data(
    third_pay_id="test_pay_123",  # From payment response
    third_id="OREN250828330246",  # Auto-generated or custom
    mobile_model_id="MM020250224000010",
    mobile_shell_id="MS102503270003",
    pic="https://example.com/test-image.jpg",
    device_id="CXYLOGD8OQUK"
)
```

### CLI Usage

```bash
# Run comprehensive test
python chinese_api.py test

# Get brands only
python chinese_api.py brands

# Get shops
python chinese_api.py shops

# Get stock for specific brand
python chinese_api.py stock --brand-id BR20250111000002

# Get goods for specific shop
python chinese_api.py goods --shop-id SP102507070001

# Test payment
python chinese_api.py pay --mobile-model-id MM020250224000010

# Report order information
python chinese_api.py order --third-pay-id test_pay_123 --mobile-model-id MM020250224000010 --mobile-shell-id MS102503270003 --pic "https://example.com/test-image.jpg"
```

## 7. Environment Variables

```bash
export CH_API_BASE_URL="http://app-dev.deligp.com:8500/mobileShell/en"
export CH_API_ACCOUNT="your_account"
export CH_API_PASSWORD="your_password"
export CH_API_DEVICE_ID="CXYLOGD8OQUK"
```
