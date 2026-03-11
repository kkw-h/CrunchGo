# CrunchGo API 接口设计文档

本文档描述了 CrunchGo 街边点餐系统的后端 API 接口定义。
**Base URL**: `/api/v1`

## 1. 认证模块 (Auth)

### 1.1 小程序登录
- **接口**: `POST /auth/login`
- **描述**: 使用微信 `login` 获取的 `code` 换取后端登录凭证（JWT）。
- **Request**:
  ```json
  {
    "code": "081......" // wx.login 获取的临时凭证
  }
  ```
- **Response**:
  ```json
  {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR...",
    "expiresIn": 3600,
    "user": {
      "id": "u_12345",
      "nickname": "WeChatUser"
    }
  }
  ```

## 2. 商品模块 (Product)

### 2.1 获取菜单列表
- **接口**: `GET /products`
- **描述**: 获取所有上架商品，按分类聚合。
- **Response**:
  ```json
  [
    {
      "id": 1,
      "name": "招牌咖啡",
      "sort": 1,
      "products": [
        {
          "id": 101,
          "name": "冰美式",
          "price": 1500, // 单位：分
          "image": "https://...",
          "stock": 100,
          "tags": ["推荐", "冰"],
          "specs": [
            { "name": "糖度", "options": ["无糖", "半糖", "全糖"] }
          ]
        }
      ]
    }
  ]
  ```

### 2.2 获取商品详情
- **接口**: `GET /products/:id`
- **描述**: 获取单个商品的详细信息（用于独立详情页）。

## 3. 订单模块 (Order)

### 3.1 创建订单
- **接口**: `POST /orders`
- **Auth**: Required
- **Request**:
  ```json
  {
    "items": [
      {
        "productId": 101,
        "quantity": 1,
        "specs": { "糖度": "半糖" }
      },
      {
        "productId": 102,
        "quantity": 2
      }
    ],
    "notes": "不要吸管"
  }
  ```
- **Response**:
  ```json
  {
    "orderId": "ORD_20231027_0001",
    "totalAmount": 4500, // 45.00元
    "status": "PENDING",
    "createdAt": "2023-10-27T10:00:00Z"
  }
  ```

### 3.2 获取订单详情
- **接口**: `GET /orders/:id`
- **Auth**: Required
- **Response**:
  ```json
  {
    "id": "ORD_20231027_0001",
    "status": "PAID", // PENDING, PAID, PREPARING, READY, COMPLETED, CANCELLED
    "queueNumber": "A102", // 取餐号 (仅 PAID 后生成)
    "items": [...],
    "timeline": {
      "created": "...",
      "paid": "..."
    }
  }
  ```

### 3.3 获取历史订单
- **接口**: `GET /orders`
- **Auth**: Required
- **Query Params**: `page=1&limit=10&status=PAID`

## 4. 支付模块 (Payment)

### 4.1 发起支付
- **接口**: `POST /orders/:id/pay`
- **Auth**: Required
- **描述**: 获取微信支付所需的签名参数。
- **Response**:
  ```json
  {
    "timeStamp": "1698372819",
    "nonceStr": "5K8264ILTKCH16CQ2502SI8ZNMTM67VS",
    "package": "prepay_id=wx27101339...",
    "signType": "RSA",
    "paySign": "oR9d8..."
  }
  ```

### 4.2 支付回调 (Webhook)
- **接口**: `POST /payment/callback/wechat`
- **描述**: 接收微信支付服务器的异步通知。
- **注意**: 需验证微信签名，处理幂等性。

## 5. 排队与店铺状态 (Queue)

### 5.1 获取排队状态
- **接口**: `GET /shop/queue-status`
- **Response**:
  ```json
  {
    "waitingOrders": 5, // 当前制作中+待制作订单数
    "estimatedWaitMinutes": 15, // 预估等待时间
    "isOpen": true, // 店铺营业状态
    "notice": "今日招牌柠檬茶已售罄" // 店铺公告
  }
  ```

## 6. 商家管理端 (Admin)

### 6.1 商家登录
- **接口**: `POST /admin/login`

### 6.2 商家订单管理
- **接口**: `GET /admin/orders` (支持按状态筛选)
- **接口**: `PATCH /admin/orders/:id/status`
- **Request**:
  ```json
  {
    "status": "READY" // 变更为“请取餐”
  }
  ```
  *变更状态时，若为 READY，系统将触发订阅消息通知用户。*

### 6.3 商品库存管理
- **接口**: `PATCH /admin/products/:id/stock`
- **Request**: `{ "stock": 0 }` (快速沽清)
