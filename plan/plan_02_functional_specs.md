---
level: 2
file_id: plan_02
parent: plan_01
status: pending
created: 2026-03-09 10:00
---

# 功能规格说明书 (Functional Specs)

## 1. 核心业务流程
本系统核心在于解决“高峰期快速点餐”与“后厨自动化接单”。

### 用户点餐主流程 (User Order Flow)

```mermaid
flowchart TD
    Start(用户打开小程序) --> Login{是否登录?}
    Login -- 否 --> WXLogin[微信一键登录]
    WXLogin --> GetInfo[获取/创建会员档案]
    Login -- 是 --> Home[首页/点餐页]
    GetInfo --> Home
    
    Home --> Browse[浏览分类/菜品]
    Browse --> Select[选择规格/SKU]
    Select --> AddCart[加入购物车]
    AddCart --> ViewCart[查看购物车]
    ViewCart --> Submit[提交订单]
    
    Submit --> CheckStock{Redis 库存检查}
    CheckStock -- 不足 --> Prompt[提示售罄] --> ViewCart
    CheckStock -- 充足 --> CreateOrder[创建待支付订单]
    CreateOrder --> LockStock[Redis 锁定库存]
    
    LockStock --> Pay[发起微信支付]
    Pay -- 成功 --> UpdateStatus[更新订单: 已支付]
    Pay -- 失败/取消 --> UnlockStock[释放库存] --> End
    
    UpdateStatus --> AddPoints[增加会员积分]
    UpdateStatus --> CloudPrint[触发云打印]
    UpdateStatus --> Notify[发送订阅消息]
    
    CloudPrint --> PrintSuccess{打印成功?}
    PrintSuccess -- 是 --> Kitchen[后厨制作]
    PrintSuccess -- 否 --> AdminAlert[后台告警]
    
    Kitchen --> Pickup[用户取餐/堂食] --> End((流程结束))
```

## 2. 模块功能详解

### 2.1 用户端 (Mini Program)
*   **身份识别**：基于 `openid` 自动登录，静默注册。
*   **点餐模式**：
    *   **堂食**：选择桌号（可选）或直接下单（凭流水号取餐）。
    *   **自提**：预约时间（可选），生成取餐码。
*   **菜单展示**：支持二级分类锚点导航，支持多规格（如：辣度、加料）。
*   **订单中心**：查看进行中订单、历史订单、申请退款（仅限未制作/待接单状态，具体策略可配置）。

### 2.2 订单与支付 (Order & Pay)
*   **防超卖机制**：下单时在 Redis 中 `decr` 库存，支付超时（如 15分钟）自动归还。
*   **支付状态机**：
    *   `PENDING` (待支付)
    *   `PAID` (已支付/制作中)
    *   `COMPLETED` (已完成)
    *   `CANCELLED` (已取消/超时)
    *   `REFUNDING` (退款中)
    *   `REFUNDED` (已退款)
*   **云打印逻辑**：
    *   监听支付成功事件 -> 组装打印模板（店铺名、流水号、菜品、备注、时间） -> 调用云打印机 API（如飞鹅/易联云）。

### 2.3 接口协作时序 (Sequence Diagram)

```mermaid
sequenceDiagram
    participant User as 用户小程序
    participant API as 后端 API
    participant Redis as Redis 缓存
    participant DB as 数据库
    participant WX as 微信支付
    participant Printer as 云打印机

    User->>API: 提交订单 (items, type)
    API->>Redis: 检查并扣减库存 (Lua脚本)
    alt 库存不足
        Redis-->>API: 失败
        API-->>User: 提示商品售罄
    else 库存充足
        API->>DB: 创建订单 (Status: PENDING)
        API-->>User: 返回订单号 & 支付参数
        
        User->>WX: 发起支付
        WX-->>User: 支付成功
        WX->>API: 支付回调 (Webhook)
        
        API->>DB: 更新订单 (Status: PAID)
        API->>DB: 生成取餐码
        API->>Redis: 记录销量
        
        par 异步处理
            API->>Printer: 发送打印指令
            Printer-->>API: 打印状态确认
        and
            API->>DB: 更新会员积分
        end
    end
```

## 3. 管理端功能 (Admin Dashboard)
*   **菜品管理**：
    *   CRUD 菜品，关联分类。
    *   设置 SKU（价格、库存、成本）。
    *   上下架控制。
*   **订单管理**：
    *   实时接单列表（轮询/WebSocket）。
    *   主动退款审核。
    *   补打小票功能。
*   **数据报表**：
    *   日/月销售额统计。
    *   热销菜品排行。

## 4. 异常处理与风险
| 风险点 | 触发场景 | 应对策略 |
| :--- | :--- | :--- |
| **支付回调丢失** | 网络波动/微信侧延迟 | 1. 客户端轮询查单接口<br>2. 后端定时任务主动查询微信订单状态 |
| **打印机不出单** | 设备离线/缺纸 | 1. 接口返回打印失败状态<br>2. 后台醒目提示“打印失败”<br>3. 支持手动重新下发打印 |
| **库存死锁** | 用户下单后不支付 | 设置 Redis Key 过期时间（如 15min），过期监听事件或定时任务回滚库存 |
