# Updated API

## Login

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

## Get Brand

### **Request URL**

- `brand/list`

### **Request method**

- POST

### **parameter**

Empty Object

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

## Stock Models

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
        {
            "mobile_model_name": "‌SAMSUNG Galaxy S22+",//机型名称"mobile_model_id": "MM020250120000002",//机型id"price": 10//价格-单位元"stock": 10//可用库存数量
        }
    ]
}

```

## Report Payment information

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

## Notify payment information *

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

## Get payment status

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

## Report order information

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

## Notification of order status *

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

## Get order status

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

## Get the printing list

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

## Upload files

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
    "data": "https://weburl.ndxvs.com/mobileShell/18/20250605/a0bnab9zjrku.png"//文件url
}
```