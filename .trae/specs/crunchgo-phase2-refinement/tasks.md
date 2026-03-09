# 任务清单 (Tasks)

- [x] 任务 1: 后端优化 (积分与订单)
    - [x] 子任务 1.1: 会员积分
        - [x] 创建 `UserPointLog` 模型和 Schema (user_id, amount, type: EARN/SPEND/ADJUST, description)。
        - [x] 创建 `UserPointLog` 的迁移脚本。
        - [x] 更新 `User` 模型以关联 `UserPointLog`。
        - [x] 更新 `OrderService.pay_order` 以:
            - 计算积分 (例如: 1 元 = 1 积分)。
            - 添加 `UserPointLog` 记录。
            - 更新 `User.point_balance`。
    - [x] 子任务 1.2: 每日取餐码
        - [x] 使用 Redis `INCR` 和每日过期 Key 实现 `OrderService._generate_pickup_code`。
        - [x] 更新 `OrderService.create_order` 使用新的生成器。
    - [x] 子任务 1.3: 退款逻辑
        - [x] 更新 `Order` 模型的 status 枚举，包含 `REFUNDING` (退款中), `REFUNDED` (已退款)。
        - [x] 实现 `POST /orders/{id}/refund` 接口 (用户申请退款)。
        - [x] 实现 `POST /admin/orders/{id}/refund/approve` 接口 (管理员批准退款)。
        - [x] 更新 `OrderService` 处理退款逻辑 (状态更新，如果未制作则释放库存)。

- [x] 任务 2: 管理后台仪表盘与统计
    - [x] 子任务 2.1: 统计服务
        - [x] 创建 `StatsService`，提供查询日销售额、订单数、热销商品的方法。
        - [x] 实现 `GET /admin/dashboard/stats` 接口。
    - [x] 子任务 2.2: 前端管理后台仪表盘
        - [x] 创建 `frontend-admin/src/views/dashboard/index.vue`。
        - [x] 显示关键指标 (销售额, 订单数) 和热销商品图表/列表。
        - [x] 在仪表盘或订单列表页添加退款申请列表。

- [x] 任务 3: 前端小程序增强
    - [x] 子任务 3.1: 用户积分显示
        - [x] 更新 `frontend-miniapp/src/pages/user/index.vue` (如果需要则创建) 以显示积分。
        - [x] 实现 `GET /user/points/history` 接口和页面。
    - [x] 子任务 3.2: 订单详情增强
        - [x] 醒目显示取餐码 (例如: A001)。
        - [x] 为 PAID/PREPARING 状态的订单添加 "申请退款" 按钮。

# 任务依赖
- 任务 2 依赖 任务 1 (统计需要数据)。
- 任务 3 依赖 任务 1 (API 接口)。
