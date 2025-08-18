# API

# **1. Interface Prefix**

Test environment: http://app-dev.deligp.com:8500/mobileShell/en/Official

environment: Privately provided

# **2. Global Error Code**

| **Error Code** | **Error explanation** |
| --- | --- |
| 200 | Operation successful |
| 400 | Number list error (missing, format mismatch) |
| 401 | Unauthorized, token expired |
| 403 | Access restricted, authorization expired |
| 404 | Resource, service not found |
| 405 | Disallowed http methods |
| 415 | Unsupported data/menu permissions not configured |
| 500 | Internal system error |

# **3. Data Signature**

1. Signature rule: MD5 (parameter 1 + parameter 2 + … + system name + fixed value)

Description: Sort all fields by the first letter. If the first field is the same, sort by the second letter… field value concatenation + current system name + fixed value) for MD5 encryption to obtain a 32-position string as a valid certificate for data signature.

Example (taking the recent record list as an example, the request message definition is as follows):

The signature request parameter values are as follows:

{

"user_id":"USER020250118000001",

"page":1,

"rows":10

}

Current system name: mobileShell

Fixed value: shfoa3sfwoehnf3290rqefiz4efd

The signature concatenation string value is:

| **page** | **rows** | **user_id** | **System Name** | **Fixed value** |
| --- | --- | --- | --- | --- |
| 1 | 10 | USER020250118000001 | mobileShell | shfoa3sfwoehnf3290rqefiz4efd |

The signature string result is: MD5("110USER020250118000001mobileShellshfoa3sfwoehnf3290rqefiz4efd") = 85d4dabc0b38e27c382d90641eff73fd

1. Interface request transmission mode: The message header transmits the parameter sign. For example: sign = 85d4dabc0b38e27c382d90641eff73fd
2. Java example (generate signature):

/ *** Generate TreeMap according to rules

- /

public static TreeMap<String, Object> objToTreeMap(Object obj) {

TreeMap<String, Object> treeMap = new TreeMap<String, Object>();

try {

//To prevent the accuracy of floating point types, use JsonObject

JSONObject jsonObject = new JSONObject();

if (JsonUtils.isArrayJson(obj)) {

JSONArray array = JSONArray.parseArray(obj.toString());

if(null != array && !array.isEmpty()){

jsonObject = array.getJSONObject(0);

}

}else{

jsonObject = JSONObject.parseObject(obj.toString());

}

Iterator iter = jsonObject.entrySet().iterator();

while (iter.hasNext()) {

Map.Entry entry = (Map.Entry) iter.next();

Object value = null;

if (null != entry.getValue()) {

//If the value is an object or a collection, there is no need to concatenate and encrypt it with MD5

value = entry.getValue();

if (JsonUtils.isJson(value)) {

continue;

}

}

treeMap.put(entry.getKey().toString(), value);

}

} catch (Exception e) {

[log.info](http://log.info/)("System exception: " + e.getMessage());

}

return treeMap;

}

/*** 根据上一步生成TreeMap生成签名sign

- /

public static String getAllValue(TreeMap<String, Object> treeMap) {

StringBuffer stringBuffer = new StringBuffer();

for (Map.Entry<String, Object> entry : treeMap.entrySet()) {

stringBuffer.append(entry.getValue());

}

stringBuffer.append(“mobileShell”);

stringBuffer.append(“shfoa3sfwoehnf3290rqefiz4efd”);

return Md5Utils.hash(stringBuffer.toString());

}

# **4. Request Source**

1. The header of the message is passed as req_source
2. For the UK, pass en. For example: req_source = en

# **5. http request method**

Default post request method

# **6. Authentication Token**

1. How to obtain: Get a new token through the user/login interface
2. Validity period: 1440 minutes
3. Interface request transmission mode: The message header passes the parameter Authorization. For example: Authorization = eyJhbGciOiJIUzUxMiJ9.eyJtb2JpbGVTaGVsbE1lcmNoYW50X2xvZ2luX3VzZXJfa2V5OiI6IjE4MjI5Mzc5ODM0In0.tARjRmEz5-FT8S9inf1bbSpuivlM6MTvGIUMQxJOycR07Jg4YIKPg6ndxAe9dIxt7JHB3AkFDKbI6RtzycIjn
4. Flowchart:

## Diagram 1: Authentication Flow

This diagram shows the authentication process between a UK Cloud service and a Cloud service:

### Participants:

- **英国云端** (UK Cloud)
- **云端** (Cloud)

### Process Flow:

1. **Login Request** - User submits credentials (account and password)
2. **Credential Validation** - System performs two checks:
    - Validates if the account exists
    - Verifies if the password is correct
3. **Authentication Response** - Two possible outcomes:
    - **Success**: Returns authentication token
    - **Failure**: Returns failure reason
4. **API Request** - After successful authentication, user can make API calls
5. **Token Validation** - System validates the token:
    - **Valid Token**: Processes normal request
    - **Invalid Token**: Direct rejection

---

# **5. Project Flowchart**

# System Architecture Sequence Diagrams

## Diagram 2: E-commerce Payment and Order Processing Flow

This diagram illustrates a complex e-commerce system with payment processing across three main components:

### Participants:

- **英国云端** (UK Cloud)
- **中国云端** (China Cloud)
- **机器** (Machine/Device)

### Process Flow:

### Product Information Exchange:

1. **Product Brand Information** - UK Cloud sends brand details (brand ID, brand name, etc.)
2. **Product Database Query** - Retrieves product model information from database (model ID, model name, price, inventory)

### Payment Processing:

1. **Payment Information Submission** - Sends payment details (device ID, model ID, third-party payment ID, payment amount, payment type)
2. **Payment Notification** - Forwards payment information to the machine (enNoticePayStatus command)
3. **Payment Result** - Machine returns payment status (enPayStatus command)
4. **Payment Status Notification** - China Cloud notifies UK Cloud of payment status (third-party payment ID, payment amount, payment type, payment status, payment time)

### Order Management:

1. **Payment Status Query** - UK Cloud actively queries payment status (third-party payment ID, payment amount, payment type, payment status, payment time)
2. **Order Information Upload** - Sends order details (device ID, model ID, third-party payment ID, third-party order ID, image)
3. **Order Information Notification** - Forwards order information to machine (noticeOrderPay command)
4. **Order Status** - Machine processes order status (checkPrint, print, getStock, mdfStock commands)
5. **Order Status Notification** - China Cloud notifies UK Cloud of order status (third-party order ID, status)
6. **Order Status Query** - UK Cloud actively queries order status (third-party order ID, status)

### Key Features:

- **Multi-regional Architecture**: Operates across UK and China cloud infrastructures
- **Third-party Payment Integration**: Supports external payment processors
- **Real-time Status Updates**: Bidirectional communication for payment and order status
- **Inventory Management**: Includes stock checking and modification
- **Device Integration**: Direct communication with physical machines/devices
- **Comprehensive Logging**: Tracks all transactions with unique IDs

---

**Log in**

### **Request URL**

- `user/login`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| account | yes | string | account |
| password | yes | string | password |

### **Parameter Examples**

```json
{
    "account": "188xxxxxxxx",//账号"password": "123456"//密码
}

```

### **Response results**

| **Parameter name** | **type** | **illustrate** |
| --- | --- | --- |
| id | string | User ID |
| account | string | account |
| token | string | Authentication token (valid for 1440 minutes) |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": {
        "id": "MEA020250118000001",//用户id"account": "188xxxxxxxx",//账号"token": "eyJhbGciOiJIUzUxMiJ9.eyJtb2JpbGVTaGVsbE1lcmNoYW50X2xvZ2luX3VzZXJfa2V5OiI6IjE4MjI5Mzc5ODM0In0.tARjRmEz5FT8S9inf1bbSpuivlM6MTvGIUMQxJOycR07Jg4YIKPg6ndxAe9dIxt7JHB3AkFDKbI6RtzycIjnA"//鉴权token（有效期1440分钟）
    }
}

```

---

Get Brand

### **Request URL**

- `brand/list`

### **Request method**

- POST

### **parameter**

No parameter value

### **Parameter Examples**

```json
{}

```

### **Response results**

| **Parameter name** | **type** | **illustrate** |
| --- | --- | --- |
| name | string | Brand Name |
| e_name | string | Brand English name |
| id | string | Brand ID |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {"name": "三星",//品牌名称"e_name": "SAMSUNG",//品牌英文名称"id": "BR020250120000001"//品牌id
        }
    ]
}

```

---

Stock model

### **Request URL**

- `stock/list`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| device_id | yes | string | Device ID |
| brand_id | yes | string | Brand ID |

### **Parameter Examples**

```json
{
    "device_id":"",//设备id"brand_id":""//品牌id
}

```

### **Response results**

| **Parameter name** | **type** | **illustrate** |
| --- | --- | --- |
| mobile_model_name | string | Model Name |
| mobile_model_id | string | Model ID |
| price | double | Price-Unit Yuan |
| stock | int | Available stock quantity |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {"mobile_model_name": "‌SAMSUNG Galaxy S22+",//机型名称"mobile_model_id": "MM020250120000002",//机型id"price": 10//价格-单位元"stock": 10//可用库存数量
        }
    ]
}

```

---

Report payment information

### **Request URL**

- `order/payData`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| mobile_model_id | yes | string | Model ID |
| device_id | yes | string | Device ID |
| third_id | yes | string | Third-party payment ID (rule: PYEN+yyMMdd+6 digits. For example: PYEN250604000001) |
| pay_amount | yes | double | Payment amount |
| pay_type | yes | int | Payment method0Other1WeChat2Alipay3Unlimited Pay4Cash5NAYAX6Card 7On-site payment |

### **Parameter Examples**

```json
{
    "mobile_model_id": "MM20250108000001",//机型id"device_id":"",//设备id"third_id":"",//第三方支付id"pay_amount":1,//支付金额"pay_type":1//支付方式 0其他 1微信 2支付宝 3云闪付 4现金 5NAYAX 6刷卡 7现场支付
}

```

### **Response results**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| id | yes | string | Payment ID |
| third_id | yes | string | Third-party order ID |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": {
        "id": "",//支付id"third_id": ""//第三方支付id
    }
}

```

---

Notify payment information

### **Request URL**

- `提供接口过来通知实时支付状态`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| third_id | yes | string | Third-party payment ID |
| pay_type | yes | int | Payment method0Other1WeChat2Alipay3Unlimited Pay4Cash5NAYAX6Card 7Offline payment |
| pay_amount | yes | double | Payment amount |
| pay_date | yes | string | Payment Time |
| status | yes | int | Payment status 1 Waiting for payment 2 Paying 3 Paid 4 Payment failed 5 Payment abnormal |

### **Parameter Examples**

```json
[
    {"third_id": "",//第三方支付id"pay_type": 1,//支付方式  0其他 1微信 2支付宝 3云闪付 4现金 5NAYAX 6刷卡 7线下支付"pay_amount":1.1,//支付金额"pay_date": "2025-04-10 17:18:55",//支付时间"status": 0//支付状态  1待支付 2支付中 3已支付 4支付失败 5支付异常
    }
]

```

### **Response results**

| **Parameter name** | **type** | **illustrate** |
| --- | --- | --- |
| data | string | Success (no more notification after success) Failure (maximum 10 notifications - once every 5-10 seconds) |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": "success"//成功success（成功后不再通知）   失败fail（最多通知10次-间隔5-10秒通知一次））
}

```

---

get payment status

### **Request URL**

- `order/getPayStatus`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| third_id | yes | list | Third-party payment ID collection |

### **Parameter Examples**

```json
[
    "P000001",
    "P000002"
]

```

### **Response results**

| **Parameter name** | **type** | **illustrate** |
| --- | --- | --- |
| third_id | string | Third-party payment ID |
| status | int | Payment status 1 Waiting for payment 2 Paying 3 Paid 4 Payment failed 5 Payment abnormal |

### **Response result example**

```cpp
{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {"third_id":"",//第三方支付id"status" 1//支付状态  1待支付 2支付中 3已支付 4支付失败 5支付异常
        }
    ]
}

```

---

Report Order information

### **Request URL**

- `order/orderData`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| third_pay_id | yes | string | Third-party payment ID |
| third_id | yes | string | Third-party order ID (rule: OREN+yyMMdd+6 digits. For example: OREN250604000001) |
| mobile_model_id | yes | string | Model ID |
| pic | yes | string | Print image url |
| device_id | yes | string | Device ID |

### **Parameter Examples**

```json
{
    "third_pay_id": "",//第三方支付id"third_id": "",//第三方订单id"mobile_model_id": "",//机型id"pic":"",//打印图片url"device_id":""//设备id
}

```

### **Response results**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| id | yes | string | Order ID |
| third_id | yes | string | Third-party order ID |
| queue_no | yes | string | Queue Number |
| status | yes | int | Order status 1 Waiting for payment 2 Cancelled 3 Paying 4 Paid 5 Payment failed 6 Refunding 7 Refund 8 Waiting for printing 9 Picking up 10 Pickup completed 11 Printing 12 Printed 13 Printing failed 14 Printing canceled 15 Shipping 16 Shipping completed |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": {
        "id": "",//订单id"third_id": "",//第三方订单id"queue_no": "",//队列号"status": 0//订单状态 1待付款 2已取消 3支付中 4已支付 5付款失败 6退款中 7已退款 8待打印 9取件中 10取件完成 11打印中 12已打印 13打印失败 14打印取消 15出货中 16出货完成
    }
}

```

---

notification of order status

### **Request URL**

- `提供接口过来通知实时订单状态`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| third_id | yes | string | Third-party order ID |
| status | yes | int | Order status 1 Waiting for payment 2 Cancelled 3 Paying 4 Paid 5 Payment failed 6 Refunding 7 Refund 8 Waiting for printing 9 Picking up 10 Pickup completed 11 Printing 12 Printed 13 Printing failed 14 Printing canceled 15 Shipping 16 Shipping completed |

### **Parameter Examples**

```json
[
    {"third_id": "",//第三方订单id"status": 0//订单状态 1待付款 2已取消 3支付中 4已支付 5付款失败 6退款中 7已退款 8待打印 9取件中 10取件完成 11打印中 12已打印 13打印失败 14打印取消 15出货中 16出货完成
    }
]

```

### **Response results**

| **Parameter name** | **type** | **illustrate** |
| --- | --- | --- |
| data | string | Success (no more notification after success) Failure (maximum 10 notifications - once every 5-10 seconds) |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": "success"//成功success（成功后不再通知）   失败fail（最多通知10次-间隔5-10秒通知一次）
}

```

---

Get order status

### **Request URL**

- `order/getOrderStatus`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| third_id | yes | list | Third-party order ID collection |

### **Parameter Examples**

```json
[
    "MSOR10250321000119",
    "MSOR10250321000118"
]

```

### **Response results**

| **Parameter name** | **type** | **illustrate** |
| --- | --- | --- |
| third_id | string | Third-party order ID |
| status | int | Order status 1 Waiting for payment 2 Cancelled 3 Paying 4 Paid 5 Payment failed 6 Refunding 7 Refund 8 Waiting for printing 9 Picking up 10 Pickup completed 11 Printing 12 Printed 13 Printing failed 14 Printing canceled 15 Shipping 16 Shipping completed |

### **Response result example**

```cpp
{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {"third_id":"",//第三方订单id"status" 1//订单状态 1待付款 2已取消 3支付中 4已支付 5付款失败 6退款中 7已退款 8待打印 9取件中 10取件完成 11打印中 12已打印 13打印失败 14打印取消 15出货中 16出货完成
        }
    ]
}

```

---

Get printing list

### **Request URL**

- `order/printList`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| device_id | yes | string | Device ID |

### **Parameter Examples**

```json
{
    "device_id":""//设备id
}

```

### **Response results**

| **Parameter name** | **type** | **illustrate** |
| --- | --- | --- |
| mobile_model_name | string | Model Name |
| id | string | Order ID |
| third_id | string | Third-party order ID |
| pic | string | picture |
| queue_no | string | Queue Number |
| status | string | Order status 1 Waiting for payment 2 Cancelled 3 Paying 4 Paid 5 Payment failed 6 Refunding 7 Refund 8 Waiting for printing 9 Picking up 10 Pickup completed 11 Printing 12 Printed 13 Printing failed 14 Printing canceled 15 Shipping 16 Shipping completed |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {"mobile_model_name": "2",//机型名称"id": "",//订单id"third_id":"",//第三方订单id"pic": "",//图片"queue_no":"",//队列号"status": 0//订单状态 1待付款 2已取消 3支付中 4已支付 5付款失败 6退款中 7已退款 8待打印 9取件中 10取件完成 11打印中 12已打印 13打印失败 14打印取消 15出货中 16出货完成
        }
    ]
}

```

---

Upload files

### **Request URL**

- `file/upload`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| file | yes | file | document |
| type | yes | int | Photo type: 23 British pictures |

### **Parameter Examples**

```
file 文件流
type = 23

```

### **Response results**

| **Parameter name** | **type** | **illustrate** |
| --- | --- | --- |
| data | string | File url |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": "<https://weburl.ndxvs.com/mobileShell/18/20250605/a0bnab9zjrku.png>"//文件url
}
```

---

**Get the store list**

### **Request URL**

- `shop/list`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| page | yes | int | Current Page |
| rows | yes | int | Display number of items |

### **Parameter Examples**

```json
{
    "page":1,
    "rows":10
}
```

### **Response results**

(If the response fails, multiple notifications are required)

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": {
        "total": 1,//总条数"list": [
            {"name": "Roni商店",//店铺名称"id": "SP102507070001"//店铺id
            }
        ]
    }
}
```

---

**14. Get product list**

### **Request URL**

- `goods/list`

### **Request method**

- POST

### **parameter**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| shop_id | yes | string | Store ID |

### **Parameter Examples**

```json
{
    "shop_id":""//店铺id
}
```

### **Response results**

| **Parameter name** | **Required** | **type** | **illustrate** |
| --- | --- | --- | --- |
| shell_classify_id | yes | string | Mobile phone case classification id |
| shop_id | yes | string | Store ID |
| mobile_shell_id | yes | string | Phone case ID |
| mobile_model_name | yes | string | Model Name |
| brand_ename | yes | string | Brand Name |
| mobile_shell_name | yes | string | Phone case name |
| mobile_shell_sku | yes | string | Mobile phone case sku |
| id | yes | string | Product ID |
| shell_classify_ename | yes | string | Mobile phone case category name |
| mobile_model_id | yes | string | Model ID |
| brand_id | yes | string | Brand ID |

### **Response result example**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {"shell_classify_id": "MS102503180003",//手机壳分类id"shop_id": "SP102507070001",//店铺id"mobile_shell_id": "MS102503270003",//手机壳id"mobile_model_name": "iPhone 15 Pro",//机型名称"brand_ename": "Apple",//品牌名称"mobile_shell_name": "iPhone15 Pro 基础版",//手机壳名称"mobile_shell_sku": "",//手机壳sku"id": "G102507290004",//商品id"shell_classify_ename": null,//手机壳分类名称"mobile_model_id": "MM020250224000010",//机型id"brand_id": "BR20250111000002"//品牌id
        }
    ]
}
```

This is how i did it

```bash
import requests
import hashlib
import json
from datetime import datetime
from dataclasses import dataclass
import time

@dataclass
class ChineseAPIConfig:
    """Configuration for Chinese API"""
    base_url: str = "http://app-dev.deligp.com:8500/mobileShell/en"
    account: str = "taharizvi.ai@gmail.com"
    password: str = "EN112233"
    system_name: str = "mobileShell"
    fixed_key: str = "shfoa3sfwoehnf3290rqefiz4efd"
    device_id: str = "1CBRONIQRWQQ"
    timeout: int = 30

class ChineseAPIClient:
    """Simple client for Chinese API"""
    
    def __init__(self, config: ChineseAPIConfig):
        self.config = config
        self.token = None
        self.session = requests.Session()
    
    def generate_signature(self, params: dict) -> str:
        """Generate MD5 signature for API request"""
        # Sort parameters by key
        sorted_params = dict(sorted(params.items()))
        
        # Concatenate values
        signature_string = ""
        for key in sorted(sorted_params.keys()):
            value = sorted_params[key]
            if value is not None:
                signature_string += str(value)
        
        # Add system name and fixed key
        signature_string += self.config.system_name
        signature_string += self.config.fixed_key
        
        print(f"Signature string: {signature_string}")
        
        # Generate MD5 hash
        signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()
        print(f"Generated signature: {signature}")
        
        return signature
    
    def login(self) -> bool:
        """Login and get authentication token"""
        print("Logging in...")
        
        login_data = {
            "account": self.config.account,
            "password": self.config.password
        }
        
        signature = self.generate_signature(login_data)
        
        headers = {
            "Content-Type": "application/json",
            "sign": signature,
            "req_source": "en"
        }
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/user/login",
                json=login_data,
                headers=headers,
                timeout=self.config.timeout
            )
            
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Login response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if data.get("code") == 200:
                    self.token = data["data"]["token"]
                    print(f"Login successful! Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"Login failed - API error: {data.get('code')} - {data.get('msg')}")
            else:
                print(f"Login failed - HTTP status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return False
            
        except Exception as e:
            print(f"Login exception: {str(e)}")
            return False
    
    def test_paydata(self, mobile_model_id: str, pay_amount: float = 10.0, pay_type: int = 1) -> dict:
        """Test the order/payData endpoint"""
        print(f"\nTesting order/payData endpoint...")
        
        if not self.token:
            if not self.login():
                return {"error": "Failed to authenticate"}
        
        # Generate unique third-party ID following the rule: PYEN+yyMMdd+6 digits
        third_id = f"PYEN{datetime.now().strftime('%y%m%d')}{str(int(time.time()))[-6:]}"
        print(f"Generated third_party_id: {third_id}")
        
        payload = {
            "mobile_model_id": mobile_model_id,
            "device_id": self.config.device_id,
            "third_id": third_id,
            "pay_amount": pay_amount,
            "pay_type": pay_type
        }
        
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        signature = self.generate_signature(payload)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token,
            "sign": signature,
            "req_source": "en"
        }
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/order/payData",
                json=payload,
                headers=headers,
                timeout=self.config.timeout
            )
            
            print(f"PayData response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"PayData response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return data
            else:
                print(f"PayData failed - HTTP status: {response.status_code}")
                print(f"Response: {response.text}")
                return {"error": f"HTTP {response.status_code}", "response": response.text}
                
        except Exception as e:
            print(f"PayData exception: {str(e)}")
            return {"error": str(e)}

def test_different_scenarios():
    """Test different payment scenarios"""
    config = ChineseAPIConfig()
    client = ChineseAPIClient(config)
    
    # Test scenarios
    scenarios = [
        {
            "name": "WeChat Payment",
            "mobile_model_id": "MM020250120000002",
            "pay_amount": 10.0,
            "pay_type": 1
        },
        {
            "name": "Alipay Payment", 
            "mobile_model_id": "MM020250120000002",
            "pay_amount": 15.5,
            "pay_type": 2
        },
        {
            "name": "Cash Payment",
            "mobile_model_id": "MM020250120000002", 
            "pay_amount": 20.0,
            "pay_type": 4
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"Testing: {scenario['name']}")
        print(f"{'='*60}")
        
        result = client.test_paydata(
            mobile_model_id=scenario["mobile_model_id"],
            pay_amount=scenario["pay_amount"],
            pay_type=scenario["pay_type"]
        )
        
        results.append({
            "scenario": scenario["name"],
            "result": result
        })
        
        # Wait between requests
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        scenario_name = result["scenario"]
        response = result["result"]
        
        if "error" in response:
            print(f"❌ {scenario_name}: FAILED - {response['error']}")
        elif response.get("code") == 200:
            print(f"✅ {scenario_name}: SUCCESS")
        else:
            print(f"❌ {scenario_name}: FAILED - Code: {response.get('code')} - {response.get('msg')}")

def test_device_ids():
    """Test different device ID patterns to find a valid one"""
    config = ChineseAPIConfig()
    client = ChineseAPIClient(config)
    
    # Common device ID patterns to try
    device_patterns = [
        "TEST_DEVICE_001",
        "DEVICE_001", 
        "DEV_001",
        "EN_DEVICE_001",
        "UK_DEVICE_001", 
        "MOBILE_001",
        "SHELL_001",
        "DEMO_001",
        "API_TEST_001"
    ]
    
    print(f"\n{'='*60}")
    print("TESTING DIFFERENT DEVICE IDs")
    print(f"{'='*60}")
    
    for device_id in device_patterns:
        print(f"\nTrying device ID: {device_id}")
        config.device_id = device_id
        client.config = config
        
        result = client.test_paydata("MM020250120000002")
        
        if "error" not in result and result.get("code") == 200:
            print(f"✅ SUCCESS! Valid device ID found: {device_id}")
            return device_id
        elif result.get("code") == 500 and "设备" in result.get("msg", ""):
            print(f"❌ {device_id}: Unauthorized")
        else:
            print(f"⚠️  {device_id}: Other error - {result.get('msg', 'Unknown')}")
    
    print(f"\n❌ No valid device ID found from tested patterns")
    return None

if __name__ == "__main__":
    print("=" * 80)
    print("SIMPLE PAYDATA ENDPOINT TEST")
    print("=" * 80)
    
    config = ChineseAPIConfig()
    print(f"Base URL: {config.base_url}")
    print(f"Account: {config.account}")
    print(f"Device ID: {config.device_id}")
    
    # Single test
    client = ChineseAPIClient(config)
    result = client.test_paydata("MM020250120000002")
    
    print(f"\n{'='*60}")
    print("RESULT ANALYSIS")
    print(f"{'='*60}")
    
    if "error" in result:
        print(f"❌ TEST FAILED: {result['error']}")
    elif result.get("code") == 200:
        print(f"✅ TEST SUCCESSFUL!")
        print(f"   Payment ID: {result['data'].get('id')}")
        print(f"   Third Party ID: {result['data'].get('third_id')}")
    elif result.get("code") == 500 and "设备" in result.get("msg", ""):
        print(f"❌ DEVICE PERMISSION ERROR")
        print(f"   Error: {result.get('msg')}")
        print(f"   Your device ID '{config.device_id}' is not authorized")
        print(f"   Solutions:")
        print(f"   - Contact admin to authorize this device")
        print(f"   - Use a valid device ID")
        print(f"   - Register the device in the system")
        
        # Offer to test different device IDs
        print(f"\n🔍 Would you like to test different device ID patterns?")
        print(f"   Uncomment the line: test_device_ids()")
    else:
        print(f"❌ API ERROR: Code {result.get('code')} - {result.get('msg')}")
    
    # Uncomment to test multiple device ID patterns
    # valid_device = test_device_ids()
    
    # Uncomment to test multiple scenarios with different payment types
    # test_different_scenarios()

"""
PS P:\roni dalal complete\frontend> python .\pay_data_test.py
================================================================================
SIMPLE PAYDATA ENDPOINT TEST
================================================================================
Base URL: http://app-dev.deligp.com:8500/mobileShell/en
Account: taharizvi.ai@gmail.com
Device ID: 1CBRONIQRWQQ

Testing order/payData endpoint...
Logging in...
Signature string: taharizvi.ai@gmail.comEN112233mobileShellshfoa3sfwoehnf3290rqefiz4efd
Generated signature: a22664d06749e18629f68935d2a63755
Login response status: 200
Login response: {
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "MEA102507030002",
    "account": "taharizvi.ai@gmail.com",
    "token": "eyJhbGciOiJIUzUxMiJ9.eyJtb2JpbGVTaGVsbF9sb2dpbl91c2VyX2tleToiOiJ0YWhhcml6dmkuYWlAZ21haWwuY29tIn0.jUNZ4VRJJ1eCpwGckFoI9SlP3yXabvWx5Zy29rQWC7mcAPgXg2mH53zOj-fHExapih5mvRtBwJPsUIK2IX_zsg"
  }
}
Login successful! Token: eyJhbGciOiJIUzUxMiJ9...
Generated third_party_id: PYEN250811908177
Payload: {
  "mobile_model_id": "MM020250120000002",
  "device_id": "1CBRONIQRWQQ",
  "third_id": "PYEN250811908177",
  "pay_amount": 10.0,
  "pay_type": 1
}
Signature string: 1CBRONIQRWQQMM02025012000000210.01PYEN250811908177mobileShellshfoa3sfwoehnf3290rqefiz4efd
Generated signature: 7c11e62fd28064277076ae66c514d891
PayData response status: 200
PayData response: {
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "MSPY10250811000008",
    "third_id": "PYEN250811908177"
  }
}

============================================================
RESULT ANALYSIS
============================================================
✅ TEST SUCCESSFUL!
   Payment ID: MSPY10250811000008
   Third Party ID: PYEN250811908177
"""
```