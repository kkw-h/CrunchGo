# CrunchGo 项目启动指南

## 1. 环境准备
确保本地已安装：
- Docker & Docker Compose
- Python 3.10+
- Node.js 16+

## 2. 启动基础服务 (PostgreSQL & Redis)
在项目根目录下运行：
```bash
docker-compose up -d
```
如果启动失败，请检查 Docker Desktop 是否已运行。

## 3. 后端服务 (Backend)
进入 `backend` 目录：
```bash
cd backend
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
# 安装依赖
pip install -r requirements.txt
# 运行数据库迁移 (需确保 Docker 已启动)
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 4. 前端小程序 (Frontend MiniApp)
进入 `frontend-miniapp` 目录：
```bash
cd frontend-miniapp
# 安装依赖
npm install
# 启动开发服务器 (微信小程序)
npm run dev:weapp
```
然后使用微信开发者工具导入 `frontend-miniapp/dist` 目录。

## 5. 管理后台 (Frontend Admin)
进入 `frontend-admin` 目录：
```bash
cd frontend-admin
# 安装依赖
npm install
# 启动开发服务器
npm run dev
```
访问 `http://localhost:5173`。

## 6. 测试与验证
### 自动化端到端测试
在启动后端服务后，可以运行 E2E 测试脚本来验证核心业务流程（下单、支付、积分、退款等）：

```bash
# 确保已安装测试依赖
pip install httpx

# 运行测试脚本
python backend/tests/e2e_test.py
```

### 模拟环境说明
- **支付**: 系统目前使用 Mock 支付，调用 `/pay` 接口会直接成功并更新状态。
- **打印**: 未配置打印机时，打印内容会输出到后端日志中。

## 7. 注意事项
- **数据库连接**: 默认配置为 `postgresql://postgres:postgres@localhost:5432/crunchgo`。
- **Redis 连接**: 默认配置为 `redis://localhost:6379/0`。
- **云打印**: 请在 `backend/app/core/config.py` 中配置 `PRINTER_USER`, `PRINTER_UKEY`, `PRINTER_SN`。
- **微信支付**: 需配置 `WECHAT_APP_ID`, `WECHAT_MCH_ID` 等环境变量。
