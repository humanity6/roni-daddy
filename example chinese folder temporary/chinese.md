# Chinese API Documentation

## 1. Interface Configuration

**Test Environment:** `http://app-dev.deligp.com:8500/mobileShell/en`

**System Configuration:**
- System Name: `mobileShell`
- Fixed Key: `shfoa3sfwoehnf3290rqefiz4efd`
- Request Source: `en`

## 2. Global Error Codes

| Code | Description |
|------|-------------|
| 200  | Operation successful |
| 400  | Parameter error (missing, format mismatch) |
| 401  | Unauthorized, token expired |
| 403  | Access restricted, authorization expired |
| 404  | Resource/service not found |
| 500  | Internal system error |

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
- `sign`: The MD5 signature
- `req_source`: `en`
- `Authorization`: Token (for authenticated endpoints)
- `Content-Type`: `application/json`

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

**Request:**
```json
{
  "device_id": "1CBRONIQRWQQ",
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
      "mobile_model_name": "iPhone 16 Pro Max",
      "mobile_model_id": "MM1020250226000002",
      "price": "100",
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
      "mobile_shell_id": "MS102503270003",
      "mobile_model_name": "iPhone 15 Pro",
      "brand_ename": "Apple",
      "mobile_shell_name": "iPhone15 Pro 基础版",
      "mobile_shell_sku": "IP111",
      "id": "G102507290004",
      "mobile_model_id": "MM020250224000010",
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
  "mobile_model_id": "MM1020250226000002",
  "device_id": "1CBRONIQRWQQ",
  "third_id": "PYEN250811908177",
  "pay_amount": 10.0,
  "pay_type": 1
}
```

**Payment Types:**
- 0: Other
- 1: WeChat
- 2: Alipay
- 3: Flash Pay
- 4: Cash
- 5: NAYAX
- 6: Card
- 7: On-site payment

**Third ID Format:** `PYEN + yyMMdd + 6 digits`
Example: `PYEN250811908177`

**Response:**
```json
{
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "MSPY10250811000008",
    "third_id": "PYEN250811908177"
  }
}
```

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
stock = client.stock_list(device_id="1CBRONIQRWQQ", brand_id="BR20250111000002")

# Get shops
shops = client.shop_list()

# Get goods/products for a specific shop
goods = client.goods_list(shop_id="SP102507070001")

# Make payment
payment = client.pay_data(
    mobile_model_id="MM1020250226000002",
    device_id="1CBRONIQRWQQ",
    pay_amount=10.0,
    pay_type=1
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
python chinese_api.py pay --mobile-model-id MM1020250226000002
```

## 7. Environment Variables

```bash
export CH_API_BASE_URL="http://app-dev.deligp.com:8500/mobileShell/en"
export CH_API_ACCOUNT="your_account"
export CH_API_PASSWORD="your_password"
export CH_API_DEVICE_ID="1CBRONIQRWQQ"
```