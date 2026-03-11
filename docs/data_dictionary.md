# CrunchGo 数据字典 (Data Dictionary)

> **注意**: 本文档记录了 CrunchGo 项目的数据库表结构设计。每当数据库结构发生变更（如新增表、修改字段、添加索引等）时，**必须同步更新本文档**以保持一致性。

---

## 目录

1.  [Category (商品分类)](#1-category-商品分类)
2.  [Product (商品)](#2-product-商品)
3.  [Order (订单)](#3-order-订单)
4.  [OrderItem (订单项)](#4-orderitem-订单项)
5.  [枚举类型 (Enums)](#5-枚举类型-enums)

---

## 1. Category (商品分类)

*   **表名**: `categories`
*   **描述**: 存储商品的分类信息，如“咖啡”、“茶饮”、“甜点”等。

| 字段名 | 类型 | 必填 | 默认值 | 描述 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `int` | 是 | Auto Increment | 主键 ID | |
| `name` | `varchar(50)` | 是 | - | 分类名称 | |
| `sort` | `int` | 否 | `0` | 排序权重 | 数字越大越靠前或按需排序 |
| `isActive` | `boolean` | 否 | `true` | 是否启用 | 软删除或禁用标记 |
| `createdAt` | `timestamp` | 是 | `now()` | 创建时间 | |
| `updatedAt` | `timestamp` | 是 | `now()` | 更新时间 | |

---

## 2. Product (商品)

*   **表名**: `products`
*   **描述**: 存储具体的商品信息。

| 字段名 | 类型 | 必填 | 默认值 | 描述 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `int` | 是 | Auto Increment | 主键 ID | |
| `name` | `varchar(100)` | 是 | - | 商品名称 | |
| `description` | `varchar` | 否 | `null` | 商品描述 | |
| `price` | `decimal(10,2)` | 是 | - | 单价 | |
| `stock` | `int` | 否 | `0` | 库存数量 | |
| `image` | `varchar` | 否 | `null` | 图片 URL | |
| `specs` | `jsonb` | 否 | `null` | 规格配置 | e.g. `{"temp": ["Hot"], "sugar": ["Half"]}` |
| `isAvailable` | `boolean` | 否 | `true` | 是否上架 | |
| `categoryId` | `int` | 否 | `null` | 所属分类 ID | 外键 -> `categories.id` (SET NULL) |
| `createdAt` | `timestamp` | 是 | `now()` | 创建时间 | |
| `updatedAt` | `timestamp` | 是 | `now()` | 更新时间 | |

---

## 3. Order (订单)

*   **表名**: `orders`
*   **描述**: 存储用户的订单主表信息。

| 字段名 | 类型 | 必填 | 默认值 | 描述 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `uuid` | 是 | UUID | 主键 ID | 全局唯一标识 |
| `orderNumber` | `varchar(20)` | 是 | - | 取餐号 | 每日重置，如 "A102" |
| `totalAmount` | `decimal(10,2)` | 是 | - | 订单总金额 | |
| `status` | `enum` | 否 | `PENDING` | 订单状态 | 见 [OrderStatus](#orderstatus) |
| `paymentId` | `varchar` | 否 | `null` | 支付流水号 | 微信支付单号 |
| `paidAt` | `timestamp` | 否 | `null` | 支付时间 | |
| `createdAt` | `timestamp` | 是 | `now()` | 创建时间 | 下单时间 |
| `updatedAt` | `timestamp` | 是 | `now()` | 更新时间 | |

---

## 4. OrderItem (订单项)

*   **表名**: `order_items`
*   **描述**: 存储订单中购买的具体商品及快照信息。

| 字段名 | 类型 | 必填 | 默认值 | 描述 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `int` | 是 | Auto Increment | 主键 ID | |
| `orderId` | `uuid` | 是 | - | 所属订单 ID | 外键 -> `orders.id` (CASCADE) |
| `productId` | `int` | 是 | - | 商品 ID | 外键 -> `products.id` |
| `productName` | `varchar` | 是 | - | 商品名称快照 | 购买时的名称 |
| `price` | `decimal(10,2)` | 是 | - | 单价快照 | 购买时的单价 |
| `quantity` | `int` | 是 | - | 购买数量 | |
| `options` | `jsonb` | 否 | `null` | 选定的规格 | e.g. `{"temp": "Hot", "sugar": "Half"}` |

---

## 5. 枚举类型 (Enums)

### OrderStatus

订单状态枚举，用于 `orders.status` 字段。

| 值 | 描述 |
| :--- | :--- |
| `PENDING` | **待支付**: 订单已创建，等待用户支付。 |
| `PAID` | **已支付**: 用户完成支付，等待商家接单或制作。 |
| `PREPARING` | **制作中**: 商家已接单，正在制作商品。 |
| `READY` | **请取餐**: 制作完成，通知用户取餐。 |
| `COMPLETED` | **已完成**: 订单流程结束。 |
| `CANCELLED` | **已取消**: 订单因超时未支付或用户主动取消而关闭。 |
