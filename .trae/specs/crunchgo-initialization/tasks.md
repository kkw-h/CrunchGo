# 任务清单 (Tasks)

- [x] 任务 1: 环境设置
    - [x] 子任务 1.1: 初始化 Python FastAPI 后端项目
        - [x] 创建 `backend/app` 目录结构 (api, core, models, schemas, services, utils)
        - [x] 创建 `requirements.txt` (FastAPI, Uvicorn, SQLAlchemy, Alembic, Redis)
    - [x] 子任务 1.2: 初始化前端小程序 (Taro + Vue3)
        - [x] 创建 `frontend-miniapp` 目录 (Taro Vue3 模板)
        - [x] 配置 `app.config.ts` 适配微信小程序
    - [x] 子任务 1.3: 初始化管理后台 (Vue3 + Element Plus)
        - [x] 创建 `frontend-admin` 目录 (Vue3 + Vite 模板)
        - [x] 安装 Element Plus 并配置基础布局
    - [x] 子任务 1.4: 数据库与缓存配置
        - [x] 创建 `docker-compose.yml` (PostgreSQL 和 Redis)
        - [x] 配置数据库连接环境变量 (.env)

- [x] 任务 2: 后端核心开发
    - [x] 子任务 2.1: 数据库迁移
        - [x] 定义 SQLAlchemy 模型 (`User`, `Category`, `Product`, `ProductSku`, `Order`, `OrderItem`, `Payment`)
        - [x] 配置 Alembic 并生成初始迁移脚本
        - [x] 应用迁移到 PostgreSQL
    - [x] 子任务 2.2: 认证模块
        - [x] 实现 `POST /auth/login/wechat` 接口
        - [x] 创建 `User` 服务处理微信登录和 Token 生成
    - [x] 子任务 2.3: 菜单模块
        - [x] 实现 `GET /categories`, `GET /products`, `GET /products/{id}` 接口
        - [x] 创建 `Menu` 服务获取分类和 SKU 商品
    - [x] 子任务 2.4: 订单模块 (核心逻辑)
        - [x] 实现 `POST /orders` 接口 (含 Redis 库存检查与锁定)
        - [x] 实现 `POST /orders/{order_no}/pay` 接口
        - [x] 实现 `POST /webhook/wechat/pay` 接口处理支付回调
    - [x] 子任务 2.5: 云打印集成
        - [x] 创建 `Printer` 服务对接云打印 API (飞鹅/易联云)
        - [x] 实现支付成功后触发打印逻辑

- [x] 任务 3: 前端小程序开发
    - [x] 子任务 3.1: API 客户端设置
        - [x] 封装 API 请求服务
    - [x] 子任务 3.2: 首页与菜单页
        - [x] 实现首页布局
        - [x] 实现菜单页 (分类导航 + 商品列表)
        - [x] 实现商品详情页 (SKU 选择)
    - [x] 子任务 3.3: 购物车与结算
        - [x] 实现购物车状态管理 (Pinia)
        - [x] 实现购物车页和结算流程
    - [x] 子任务 3.4: 订单管理
        - [x] 实现订单列表和订单详情页
        - [x] 实现订单状态跟踪 (轮询或 WebSocket)

- [x] 任务 4: 管理后台开发
    - [x] 子任务 4.1: 商品管理
        - [x] 实现商品列表、创建、更新、删除页面
        - [x] 实现 SKU 管理界面
    - [x] 子任务 4.2: 订单管理
        - [x] 实现订单列表 (含状态过滤)
        - [x] 实现订单详情 (含退款和补打操作)

- [x] 任务 5: 集成与验证
    - [x] 子任务 5.1: 端到端测试
        - [x] 测试全流程: 登录 -> 浏览 -> 加购 -> 结算 -> 支付 -> 打印
    - [x] 子任务 5.2: 性能测试
        - [x] 测试高并发订单创建 (验证 Redis 锁机制)

# 任务依赖
- 任务 2 依赖 任务 1
- 任务 3 依赖 任务 2 (API 接口)
- 任务 4 依赖 任务 2 (API 接口)
- 任务 5 依赖 任务 3 和 任务 4
